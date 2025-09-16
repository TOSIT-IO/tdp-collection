# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

from ansible.errors import AnsibleError

def access_fqdn(host, hostvars):
    if 'access_fqdn' in hostvars[host]:
        return hostvars[host]['access_fqdn']
    elif 'domain' in hostvars[host]:
        if 'access_sn' in hostvars[host]:
            return hostvars[host]['access_sn'] + '.' + hostvars[host]['domain']
        else:
            return hostvars[host]['inventory_hostname'] + '.' + hostvars[host]['domain']
    else:
        raise AnsibleError("Required variables: `access_fqdn` or `domain`")
