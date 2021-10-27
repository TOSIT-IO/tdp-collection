#! /usr/bin/env python

def kinit(module, kinit_bin, principal = None, password = None, keytab = None, ccache = None):
    kinit_cmd = [kinit_bin]
    if principal:
        kinit_cmd.extend([principal])
    if keytab:
        kinit_cmd.extend(['-kt', keytab])
    if ccache:
        kinit_cmd.extend(['-c', ccache])
    if password and not keytab:
        module.fail_json(msg='Password authentication not supported for kinit. Use a keytab instead.')

    (rc, out, err) = module.run_command(kinit_cmd, check_rc=True)
    
    
def kdestroy(module, kdestroy_bin, ccache = None):
    kdestroy_cmd = [kdestroy_bin]
    if ccache:
        kdestroy_cmd.extend(['-c', ccache])

    (rc, out, err) = module.run_command(kdestroy_cmd, check_rc=True)
