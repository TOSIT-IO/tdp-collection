# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

import os
import tempfile
import shutil

kerberos_spec = dict(
    kerberos=dict(type='bool', default=False),
    kinit_bin=dict(type='path', default='kinit'),
    kdestroy_bin=dict(type='path', default='kdestroy'),
    krb_principal=dict(type='str'),
    krb_keytab=dict(type='path'),
    krb_password=dict(type='str', no_log=True),
    krb_ccache=dict(type='str'),
)


def get_kinit_cmd(kinit_bin, principal=None, keytab=None, ccache=None):
    kinit_cmd = [kinit_bin]
    if principal:
        kinit_cmd.extend([principal])
    if keytab:
        kinit_cmd.extend(['-kt', keytab])
    if ccache:
        kinit_cmd.extend(['-c', ccache])
    return kinit_cmd


def kinit(module):
    if not module.params['kerberos']:
        return

    kinit_bin = module.params['kinit_bin']
    kdestroy_bin = module.params['kdestroy_bin']
    principal = module.params['krb_principal']
    keytab = module.params['krb_keytab']
    password = module.params['krb_password']
    ccache = module.params['krb_ccache']

    kinit_cmd = get_kinit_cmd(kinit_bin, principal, keytab, ccache)
    if password and not keytab:
        module.fail_json(msg='Password authentication not supported for kinit. Use a keytab instead.')

    module.run_command(kinit_cmd, check_rc=True)


def try_kinit(module, kinit_bin, kdestroy_bin, principals, keytab_path):
    """Try kinit, return True if success, False or exception otherwise"""
    # Create a tmp dir to store the krb cache in order to not override
    # an existing cache in default location
    for principal in principals:
        tmp_dir = tempfile.mkdtemp(suffix='_ansible_module_utils_kerberos')
        try:
            ccache = os.path.join(tmp_dir, "krb5cc")
            kinit_cmd = get_kinit_cmd(kinit_bin, principal, keytab_path, ccache)
            rc, stdout, stderr = module.run_command(kinit_cmd)
            if rc == 0:
                kdestroy_cmd = get_kdestroy_cmd(kdestroy_bin, ccache)
                module.run_command(kdestroy_cmd)
            else:
                return False
        finally:
            shutil.rmtree(tmp_dir)
    return True


def get_kdestroy_cmd(kdestroy_bin, ccache=None):
    kdestroy_cmd = [kdestroy_bin]
    if ccache:
        kdestroy_cmd.extend(['-c', ccache])
    return kdestroy_cmd


def kdestroy(module):
    if not module.params['kerberos']:
        return

    kinit_bin = module.params['kinit_bin']
    kdestroy_bin = module.params['kdestroy_bin']
    principal = module.params['krb_principal']
    keytab = module.params['krb_keytab']
    password = module.params['krb_password']
    ccache = module.params['krb_ccache']

    kdestroy_cmd = get_kdestroy_cmd(kdestroy_bin, ccache)

    module.run_command(kdestroy_cmd, check_rc=True)
