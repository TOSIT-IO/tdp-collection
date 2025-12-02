#!/usr/bin/python
# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.tosit.tdp.plugins.module_utils.kerberos import list_not_working_principals_in_keytab

def main():
    argument_spec = dict(
        kinit_bin=dict(type='path', default='kinit'),
        kdestroy_bin=dict(type='path', default='kdestroy'),
        principal=dict(type='list', elements='str', required=True),
        path=dict(type='path', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        add_file_common_args=True,
        supports_check_mode=True,
    )

    kinit_bin = module.params['kinit_bin']
    kdestroy_bin = module.params['kdestroy_bin']
    principals = module.params['principal']
    keytab_path = module.params['path']

    try:
        results = {
            'changed': False,
        }

        not_working_principals = list_not_working_principals_in_keytab(module, kinit_bin, kdestroy_bin, principals, keytab_path)
        if len(not_working_principals) > 0:
            raise RuntimeError("Keytab '{}' with principal '{}' is not working".format(keytab_path, not_working_principals))

        module.exit_json(**results)

    except Exception:
        import traceback
        module.fail_json(msg=to_native(traceback.format_exc()))

if __name__ == '__main__':
    main()
