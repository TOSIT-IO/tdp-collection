#! /usr/bin/env python
# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.tosit.tdp.plugins.module_utils.kerberos_admin import kerberos_admin_spec, kadmin

def main():
    argument_spec = dict(
        principal=dict(type='str', required=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        **kerberos_admin_spec
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    principal = module.params['principal']
    state = module.params['state']

    try:
        results = {
            'changed': False,
        }
        current_state = None

        rc, stdout, stderr = kadmin(module, ['-q', 'getprinc {}'.format(principal)])
        if 'Principal does not exist' in stderr:
            current_state = 'absent'
        else:
            current_state = 'present'

        # Case when principal does not exist
        if current_state == 'absent':
            if state == 'absent':
                return module.exit_json(**results)
            results['changed'] = True
            if not module.check_mode:
                kadmin(module, ['-q', 'addprinc -randkey {}'.format(principal)])

        # Case when principal exists and must be remove
        if current_state == 'present' and state == 'absent':
            results['changed'] = True
            if not module.check_mode:
                kadmin(module, ['-q', 'delprinc -force {}'.format(principal)])

        module.exit_json(**results)

    except Exception:
        import traceback
        module.fail_json(msg=to_native(traceback.format_exc()))

if __name__ == '__main__':
    main()
