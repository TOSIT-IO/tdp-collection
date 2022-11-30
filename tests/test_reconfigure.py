# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

def test_must_include_and_must_exclude_should_not_intersect(must_include: set, must_exclude: set):
    intersection = must_include.intersection(must_exclude)
    assert (
        intersection == set()
    ), f"must_include and must_exclude should not intersect: {', '.join(intersection)}"


def test_reconfigure_plan_has_included_services(
    service_component: str, must_include: set, deployment_service_components :list
):
    difference = must_include.difference(deployment_service_components)
    assert (
        len(difference) == 0
    ), f"{service_component} reconfiguration should include: {', '.join(difference)}"


def test_reconfigure_plan_does_not_have_excluded_services(
    service_component: str, must_exclude: set, deployment_service_components: set
):
    intersection = must_exclude.intersection(deployment_service_components)
    assert (
        len(intersection) == 0
    ), f"{service_component} reconfiguration should exclude: {', '.join(intersection)}"
