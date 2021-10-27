#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.tosit.tdp.plugins.module_utils.kerberos import kerberos_spec, kinit, kdestroy

def main():
    argument_spec = dict(
        hdfs_bin=dict(type='path'),
        hdfs_conf=dict(type='path'),
        state=dict(type='str', choices=['absent', 'directory', 'file']),
        path=dict(type='path', required=True),
        owner=dict(),
        group=dict(),
        mode=dict(),
        **kerberos_spec
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    hdfs_bin = module.params['hdfs_bin'] or '/opt/tdp/hadoop/bin/hdfs'
    hdfs_conf = module.params['hdfs_conf']
    state = module.params['state'] or 'file'
    path = module.params['path']
    owner = module.params['owner']
    group = module.params['group']
    mode = module.params['mode']


    try:
        results = {
            'changed': False,
        }

        kinit(module)

        hdfs_cmd = [hdfs_bin]
        if hdfs_conf:
            hdfs_cmd.extend(['--config', hdfs_conf])
        hdfs_cmd.append('dfs')

        current_state = None
        current_owner = None
        current_group = None
        current_mode = None

        hdfs_cmd_stat = []
        hdfs_cmd_stat.extend(hdfs_cmd)
        hdfs_cmd_stat.extend(['-stat', '%F:%u:%g:%a', path])

        rc, stdout, stderr = module.run_command(hdfs_cmd_stat, check_rc=False)
        if rc != 0:
            if 'No such file or directory' in stderr:
                current_state = 'absent'
            else:
                raise RuntimeError("Error when running cmd '{}', stdout: {}, stderr: {}"
                    .format(hdfs_cmd_stat, stdout, stderr))
        else:
            current_state, current_owner, current_group, current_mode = stdout.strip().split(':')
            if current_state == 'regular file':
                current_state = 'file'

        results['old'] = {
            'state': current_state,
            'owner': current_owner,
            'group': current_group,
            'mode': current_mode,
        }

        results['new'] = {
            'state': state,
            'owner': owner,
            'group': group,
            'mode': mode,
        }

        # Case when file in hdfs is absent
        if current_state == 'absent':
            if state == 'absent':
                return module.exit_json(**results)
            hdfs_cmd_create = []
            hdfs_cmd_create.extend(hdfs_cmd)
            if state == 'directory':
                hdfs_cmd_create.extend(['-mkdir', '-p'])
            elif state == 'file':
                hdfs_cmd_create.append('-touchz')
            hdfs_cmd_create.append(path)
            results['changed'] = True
            if not module.check_mode:
                module.run_command(hdfs_cmd_create, check_rc=True)

        # Case when file in hdfs exist and must be remove
        if current_state != 'absent' and state == 'absent':
            hdfs_cmd_remove = []
            hdfs_cmd_remove.extend(hdfs_cmd)
            hdfs_cmd_remove.extend(['-rm', '-r', '-skipTrash', path])
            results['changed'] = True
            if not module.check_mode:
                module.run_command(hdfs_cmd_remove, check_rc=True)
            return module.exit_json(**results)

        # Case when file in hdfs exist
        if current_state != 'absent' and current_state != state:
            raise RuntimeError("Can't change type '{}' to '{}' for path '{}'"
                .format(current_state, state, path))

        if owner is not None and current_owner != owner:
            hdfs_cmd_owner = []
            hdfs_cmd_owner.extend(hdfs_cmd)
            hdfs_cmd_owner.extend(['-chown', owner, path])
            results['changed'] = True
            if not module.check_mode:
                module.run_command(hdfs_cmd_owner, check_rc=True)

        if group is not None and current_group != group:
            hdfs_cmd_group = []
            hdfs_cmd_group.extend(hdfs_cmd)
            hdfs_cmd_group.extend(['-chgrp', group, path])
            results['changed'] = True
            if not module.check_mode:
                module.run_command(hdfs_cmd_group, check_rc=True)

        if mode is not None and current_mode != mode:
            hdfs_cmd_mode = []
            hdfs_cmd_mode.extend(hdfs_cmd)
            hdfs_cmd_mode.extend(['-chmod', mode, path])
            results['changed'] = True
            if not module.check_mode:
                module.run_command(hdfs_cmd_mode, check_rc=True)

        module.exit_json(**results)

    except Exception:
        import traceback
        module.fail_json(msg=to_native(traceback.format_exc()))
    finally:
        try:
            kdestroy(module)
        except Exception:
            import traceback
            module.fail_json(msg=to_native(traceback.format_exc()))

if __name__ == '__main__':
    main()
