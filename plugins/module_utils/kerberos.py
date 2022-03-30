#! /usr/bin/env python
# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0


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
