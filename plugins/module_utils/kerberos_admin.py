#! /usr/bin/env python

kerberos_admin_spec = dict(
    kadmin_bin=dict(type='path', default='kadmin'),
    admin_principal=dict(type='str'),
    admin_password=dict(type='str', no_log=True),
)


def get_kadmin_cmd(kadmin_bin, admin_principal=None, admin_password=None):
    kadmin_cmd = [kadmin_bin]
    if admin_principal:
        kadmin_cmd.extend(['-p', admin_principal])
    if admin_password:
        kadmin_cmd.extend(['-w', admin_password])
    return kadmin_cmd


def kadmin(module, args):
    kadmin_bin = module.params['kadmin_bin']
    admin_principal = module.params['admin_principal']
    admin_password = module.params['admin_password']

    kadmin_cmd = get_kadmin_cmd(kadmin_bin, admin_principal, admin_password)
    kadmin_cmd.extend(args)

    return module.run_command(kadmin_cmd, check_rc=True)

