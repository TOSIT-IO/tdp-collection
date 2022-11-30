# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

"""
This will autogenerate a list of tests depending on the input document.
The values that can be `service` or `service_component` will be referred as a service_component in
the following code for simplicity.
"""

import os
import json
from pathlib import Path

import pytest

from tdp.core.collection import Collection
from tdp.core.collections import Collections
from tdp.core.dag import Dag
from tdp.core.deployment import DeploymentPlan
from tdp.core.variables import ClusterVariables

TEST_DIR = os.path.dirname(__file__)
DEFAULT_RULES_PATH = os.path.join(TEST_DIR, "rules.json")
DEFAULT_COLLECTION_PATH = os.path.dirname(TEST_DIR)

PARAMETERS_AS_FIXTURES = frozenset({"must_include", "must_exclude"})


def pytest_addoption(parser):
    parser.addoption(
        "--rules",
        dest="rules",
        default=DEFAULT_RULES_PATH,
        type=Path,
        help="rules file path",
    )
    parser.addoption(
        "--collections-path",
        dest="collections_path",
        default=DEFAULT_COLLECTION_PATH,
        type=str,
        help=f"collections path (separated by {os.pathsep})",
    )


def parse_rules(rules_path):
    with rules_path.open() as fd:
        return json.load(fd)


def pytest_generate_tests(metafunc):
    rules = parse_rules(metafunc.config.getoption("rules"))
    parameters = {"service_component"}.union(PARAMETERS_AS_FIXTURES)
    idlist = []
    # get only fixtures used in the test, ensure service_component is the first
    argnames = sorted(
        parameters.intersection(metafunc.fixturenames),
        key=lambda param: 0 if param == "service_component" else 1,
    )
    argvalues = []  # list of every set of parameters to give to the test
    for service_component, rule in rules.items():
        # One iteration is a set of parameters to give to a test
        iteration_argvalues = []
        for fixture in argnames:
            if fixture == "service_component":
                iteration_argvalues.append(service_component)
            else:
                iteration_argvalues.append(frozenset(rule.get(fixture, frozenset())))
        # Will not add the value if only component is not null
        # therefore the test will not be generated
        if argnames[0] == "service_component":
            # if a test as the fixture `service_component`, we will generate it
            # only if any of the parameters from the rules is non null
            # the nullity check must be performed on every iteration_argalues
            # except `service_component`
            iteration_argvalues_to_test = iteration_argvalues[1:]
        else:
            # If the fixture `service_component` is missing,
            # the nullity check must be performed on the iteration_argvalues
            iteration_argvalues_to_test = iteration_argvalues

        if any(iteration_argvalues_to_test):
            # if any parameter for this iteration is not null
            # we add these operations to the parameter list
            idlist.append(service_component)
            argvalues.append(iteration_argvalues)

    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="session")


@pytest.fixture(scope="session")
def collection_list(request):
    collections_path = request.config.getoption("collections_path")
    return [Collection.from_path(split) for split in collections_path.split(os.pathsep)]


@pytest.fixture(scope="session")
def collections(collection_list):
    return Collections.from_collection_list(collection_list)


@pytest.fixture(scope="session")
def dag(collections: Collections):
    return Dag(collections)


@pytest.fixture(scope="session")
def cluster_variables(collections, tmp_path_factory):
    return ClusterVariables.initialize_cluster_variables(
        collections,
        tmp_path_factory.mktemp("tdp_vars"),
    )


@pytest.fixture(scope="session")
def deployment_plan(service_component, cluster_variables, dag):
    """Generates one reconfigure deployment plan for each service_component for the whole session"""
    service = service_component.split("_")[0]

    service_component_versions = ((service, service_component, 1),)

    component_modified = getattr(cluster_variables[service], "components_modified")

    def mock_components_modified(dag, version):
        """If the service_component is a service,
        instead returns the list of every component from the service
        """
        try:
            operation = dag.operations[service_component + "_config"]
        except KeyError:
            pytest.fail(
                f"{service_component} does not exists or does not have a config action"
            )
        if operation.is_service():
            service_operations = dag.services_operations[operation.service]
            return list(
                filter(
                    lambda operation: operation.action == "config",
                    service_operations,
                )
            )
        return [operation]

    setattr(cluster_variables[service], "components_modified", mock_components_modified)
    try:
        return DeploymentPlan.from_reconfigure(
            dag, cluster_variables, service_component_versions
        )
    finally:
        setattr(cluster_variables[service], "components_modified", component_modified)


@pytest.fixture(scope="session")
def deployment_service_components(deployment_plan):
    """Converts list of operations into a list of `service_component` for ease of testing"""
    operations = []
    for operation in deployment_plan.operations:
        name = operation.service
        if operation.component is not None:
            name += "_" + operation.component
        if not name in operations:
            operations.append(name)
    return operations
