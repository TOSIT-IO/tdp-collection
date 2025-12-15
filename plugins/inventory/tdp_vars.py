# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

import hashlib
from pathlib import Path

from ansible.errors import AnsibleParserError
from ansible.plugins.inventory import BaseFileInventoryPlugin, Cacheable, Constructable
from ansible.utils.display import Display
from ansible.utils.vars import merge_hash
from ansible_collections.tosit.tdp.plugins.module_utils.constants import PREFIX

DOCUMENTATION = """
author: TOSIT
name: tdp_vars
short_description: Loads tdp variables into inventory
description:
    - Plugin `tdp_vars` will load and merge every variables into the group `all`
extends_documentation_fragment:
  - constructed
  - inventory_cache
requirements:
  - tdp
options:
    plugin:
        description: token that ensures this is a source file for the 'tdp_vars' plugin.
        required: true
        choices: ['tosit.tdp.tdp_vars']
    tdp_vars:
        description: tdp vars location, relative to ansible working directory or absolute
        # This option is required but when it is undefined, the Ansible error is not understandable
        required: false
        type: string
        env:
            - name: TDP_VARS
        ini:
            - section: tdp
              key: vars
notes: []
"""

VARS_VERSION_KEY = PREFIX + "vars_version"

display = Display()


class InventoryModule(BaseFileInventoryPlugin, Constructable, Cacheable):
    NAME = "tosit.tdp.tdp_vars"

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        self.inventory = inventory
        self.loader = loader
        self.path = path

        self._read_config_data(path)  # loads options from the environment

        error_message_option_undefined = " ".join([
            "Missing required '{}' option for 'tdp_vars' inventory plugin.",
            "'tdp_vars' will NOT be read.",
            "Have you set the environment variable '{}' ?",
            "If your Ansible tasks does not use 'tdp_vars' it will works."
        ])

        tdp_vars = self.get_option("tdp_vars")
        if tdp_vars is None:
            display.warning(error_message_option_undefined.format("tdp_vars", "TDP_VARS"))
            return

        tdp_vars = Path(tdp_vars)

        tdp_variables = self._build_tdp_variables(tdp_vars)

        cache_key = self.get_cache_key(path)  # compute tdp_vars' cache key
        update_cache, results = self._get_cached_results(cache_key)

        if cache and not update_cache:
            update_cache = self._tdp_vars_needs_update(results, tdp_variables)

        display.v(f"cache update: {update_cache}")
        if not cache or update_cache:
            # only load variable when cache is disabled, or cache update is needed
            results = self._load_tdp_vars(tdp_variables)

        display.vvv("Adding `all` group")
        self.inventory.add_group("all")
        for group, data in results.items():
            # creates global facts, facts nomenclature is PREFIX + group, with value its tdp vars
            self.inventory.set_variable("all", group, data)

        if update_cache or (not cache and self.get_option("cache")):
            self._cache[cache_key] = results

    def _compute_service_hash(self, paths):
        """Computes hash from all files in folders"""
        hash = hashlib.sha1()
        for path in paths:
            for p in path.iterdir():
                if p.is_file():
                    hash.update(p.read_bytes())
        return hash.hexdigest()

    def _get_cached_results(self, cache_key):
        """Utility function to easily get cache results"""
        update_cache = False
        results = {}
        if self.cache:
            results = self._cache.get(cache_key)
            if results is None:
                update_cache = True
                results = {}
        return update_cache, results

    def _tdp_vars_needs_update(self, results, tdp_variables):
        """Determines whether the tdp vars must be updated or not"""
        for service, value in tdp_variables.items():
            group = PREFIX + service
            if group not in results:
                # tdp vars' service is missing in cache, cache needs update
                return True
            cache_version = results[group].get(VARS_VERSION_KEY)
            if cache_version is None or cache_version != value["version"]:
                # If there is no cache version or it differs, cache needs updates
                return True
        return False

    def _build_tdp_variables(self, tdp_vars):
        tdp_variables = {}
        # collect every paths of variables
        for path in tdp_vars.iterdir():
            if not path.exists():
                continue
            tdp_variables.setdefault(path.stem, {"paths": []})["paths"].append(path)

        # build versions for the variables
        for service_def in tdp_variables.values():
            service_def["version"] = self._compute_service_hash(service_def["paths"])

        return tdp_variables

    def _load_tdp_vars(self, tdp_vars_services):
        """Returns tdp vars in a dict of key: str, value: dict

        All groups will be merged with the variables from `all`, `tdp-cluster` and `hadoop`.

        All components will be merged with their service variables."""
        inventory_vars = {}
        merge_base = {}

        LOAD_FIRST = ("all", "tdp-cluster", "hadoop")

        for service in LOAD_FIRST:
            if service not in tdp_vars_services:
                continue
            service_def = tdp_vars_services.get(service)
            service_inventory_vars, service_vars = self._load_service(
                service_def["paths"], service_def["version"], merge_base
            )
            # First loaded services constitue the base against every other services will be merged
            merge_base = merge_hash(merge_base, service_vars)
            inventory_vars.update(service_inventory_vars)
            display.vv(service + " loaded")

        for service, service_def in tdp_vars_services.items():
            if service in LOAD_FIRST:
                # skipped because already loaded
                continue
            service_inventory_vars, _ = self._load_service(
                service_def["paths"], service_def["version"], merge_base
            )
            inventory_vars.update(service_inventory_vars)
            display.vv(service + " loaded")

        return inventory_vars

    def _load_service(self, paths, version, merge_base):
        inventory_vars = {}
        service_vars = merge_hash(merge_base, {})
        service_key = ""
        for path in paths:
            for file in sorted(path.glob("*.yml")):
                group = PREFIX + file.stem
                if group in self.inventory.groups["all"].get_vars():
                    raise AnsibleParserError(
                        f"Group {file.stem} already exists,"
                        "defining the same group multiple times isn't supported"
                    )
                data = (
                    self.loader.load_from_file(
                        str(file.absolute()), cache=True, unsafe=True
                    )
                    or {}  # empty yaml returns None
                )

                data[VARS_VERSION_KEY] = version
                data = merge_hash(inventory_vars.get(group, {}), data)
                if path.stem == file.stem:  # it's service variables
                    data = merge_hash(service_vars, data)
                    service_vars = data
                    service_key = group
                inventory_vars[group] = data

        for component in inventory_vars:
            if service_key != component:
                inventory_vars[component] = merge_hash(
                    service_vars, inventory_vars[component]
                )
        return inventory_vars, service_vars
