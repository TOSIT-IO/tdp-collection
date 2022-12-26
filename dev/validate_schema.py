# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

"""Validates tdp variables schema, JSON schema is a powerful way
to enable variable annotation and type validation to any structured data.

The different schemas will define which variables are required as well as their type.
"""


import json
import os
import sys
from pathlib import Path

import yaml
from ansible.utils.vars import merge_hash
from jsonschema import validate
from jsonschema.exceptions import ValidationError

DEV_DIR = Path(os.path.dirname(__file__))
COLLECTION = DEV_DIR.parent
TDP_VARS_DEFAULTS = COLLECTION / "tdp_vars_defaults"
TDP_VARS_SCHEMA = COLLECTION / "tdp_vars_schema"


def parse_schemas(schemas_location: Path) -> dict:
    """load all json schemas in the specified location"""
    schemas = {}

    for schema in schemas_location.glob("*.json"):
        with schema.open() as fd:
            schemas[schema.stem] = json.load(fd)
    return schemas


def validate_service_variables(service: str, schema: dict) -> bool:
    """validate a given service variables (applied on service and components)

    When the variables is about a component, the variables will be merged with the
    service variables, and validation will be performed on the result."""
    status = True
    service_vars = {}
    for vars_file in (TDP_VARS_DEFAULTS / service).glob("*.yml"):
        with vars_file.open() as fd:
            vars = yaml.safe_load(fd)
        if vars_file.stem == service:
            service_vars = vars
        else:
            vars = merge_hash(service_vars, vars)
        try:
            validate(vars, schema)
            print(vars_file, "is valid")
        except ValidationError as e:
            status = False
            print(vars_file, "is invalid, error: ", e)
    return status


def main():
    schemas = parse_schemas(TDP_VARS_SCHEMA)
    status = []
    for service, schema in schemas.items():
        status.append(validate_service_variables(service, schema))
    if not all(status):
        sys.exit(1)


if __name__ == "__main__":
    main()
