# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

from ansible.errors import AnsibleError
from ansible_collections.tosit.tdp.plugins.module_utils.access_fqdn import access_fqdn


class FilterModule(object):
    def filters(self):
        return {'access_fqdn': self.access_fqdn}

    def access_fqdn(self, host, hostvars):
        return access_fqdn(host, hostvars)
