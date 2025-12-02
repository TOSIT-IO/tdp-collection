#!/usr/bin/python
# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.tosit.tdp.plugins.module_utils.kerberos import list_not_working_principals_in_keytab
from ansible_collections.tosit.tdp.plugins.module_utils.kerberos_admin import kerberos_admin_spec, kadmin

def main():
    argument_spec = dict(
        kinit_bin=dict(type='path', default='kinit'),
        kdestroy_bin=dict(type='path', default='kdestroy'),
        principal=dict(type='list', elements='str', required=True),
        path=dict(type='path', required=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        **kerberos_admin_spec
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
    state = module.params['state']

    try:
        results = {
            'changed': False,
            'diff': {},
        }
        current_state = None

        if os.path.isdir(keytab_path):
            raise RuntimeError("Keytab '{}' is a directory".format(keytab_path))

        if os.path.exists(keytab_path):
            current_state = 'present'
        else:
            current_state = 'absent'

        if current_state == 'absent' and state == 'absent':
            return module.exit_json(**results)

        if current_state == 'present':
            # Case when keytab exists and must be remove
            if state == 'absent':
                results['changed'] = True
                if not module.check_mode:
                    os.remove(keytab_path)
                return module.exit_json(**results)
            
            not_working_principals = list_not_working_principals_in_keytab(module, kinit_bin, kdestroy_bin, principals, keytab_path)

            # Case when keytab exists, try kinit to verify if the keytab is working.
            if len(not_working_principals) == 0:
                # Update file permissions for existing keytab if needed
                file_args = module.load_file_common_arguments(module.params)
                results['changed'] = module.set_fs_attributes_if_different(
                    file_args, results['changed'], results['diff'],
                )

                return module.exit_json(**results)
            
            principals = not_working_principals

        # Either the keytab does not exist or it is not valid, so it must be generated
        results['changed'] = True
        if not module.check_mode:
            principal_args = ' '.join(set(principals))
            rc, stdout, stderr = kadmin(module, ['-q', 'ktadd -k {} {}'.format(keytab_path, principal_args)])
            # rc is 0 when the principal does not exist...
            if 'Principal' in stderr and 'does not exist' in stderr:
                raise RuntimeError("Failed to generate keytab for principal '{}': {}".format(principals, stderr))
            # Keytab generated is not guarantee to works so it must be verified,
            # for example, deleting a principal without deleting the keytab, then create the
            # same principal will reset the kvno, generate keytab in the same keytab file,
            # the keytab file will have the old kvno which is greater than the new kvno
            remaining_not_working_principals = list_not_working_principals_in_keytab(module, kinit_bin, kdestroy_bin, principals, keytab_path)
            if len(remaining_not_working_principals) > 0:
                raise RuntimeError("Keytab '{}' generated for principal '{}' is not working".format(keytab_path, remaining_not_working_principals))

        file_args = module.load_file_common_arguments(module.params)

        # Update the diff dict only if the keytab already exists,
        # there is no need to display a permission change for a newly created file
        diff = None
        if current_state == 'present':
            diff = results['diff']
        results['changed'] = module.set_fs_attributes_if_different(
            file_args, results['changed'], diff,
        )

        module.exit_json(**results)

    except Exception:
        import traceback
        module.fail_json(msg=to_native(traceback.format_exc()))

if __name__ == '__main__':
    main()
