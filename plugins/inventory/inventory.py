# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

from ansible.plugins.inventory import BaseFileInventoryPlugin, Constructable, Cacheable
from ansible.utils.display import Display
from ansible.errors import AnsibleParserError
from ansible_collections.tosit.tdp.plugins.module_utils.constants import PREFIX

import os

display = Display()


class InventoryModule(BaseFileInventoryPlugin, Constructable, Cacheable):
    NAME = "tosit.tdp.inventory"

    def verify_file(self, path):
        """return true/false if this is possibly a valid file for this plugin to consume"""
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if "tdp_vars" in str(path) and str(path).endswith((".yml", ".yaml")):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self.inventory = inventory
        self.loader = loader
        self.path = path
        filename = os.path.splitext(os.path.basename(path))[0]
        group = PREFIX + filename
        data = self.loader.load_from_file(path, cache=True, unsafe=True)
        self.inventory.add_group("all")
        if group in self.inventory.groups["all"].get_vars():
            raise AnsibleParserError(
                f"Group {filename} already exists,"
                "defining the same group multiple times isn't supported"
            )
        # creates global facts, facts nomenclature is PREFIX + group, with value data
        self.inventory.set_variable("all", group, data)
