# Ansible Knox TDP

This role deploys the Knox TDP release. It installs:

- Knox Gateway Application

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Knox TDP release .tar.gz (`knox_dist_file` role variable) file available in `files`
- Knoxshell TDP release .tar.gz (`knoxshell_dist_file` role variable) file available in `files`
- Group `knox` defined in the Ansible hosts file
- Certificate of the CA available as `root.pem` in `files`
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` available in `files`


## Example

The following hosts file and playbook are given as examples.

### Host file
```
[knox]
edge
```

### Required variables

- `realm`: Kerberos realm of the cluster
- `kadmin_principal`: admin principal used to connect kadmin service
- `kadmin_password`: passowrd of the admin principal

### Example playbook
```
- name: "Install Knox"
  hosts: knox
  tasks:
    - import_role:
        name: tosit.tdp.knox
```


## Additional notes

- Keystore creation uses `-srcalias` and `-destalias gateway-identity`
- Generate Knox master secret using interactive tool "expect"


## TODO

- [ ] Modify pom.xml, rebuild and rename release
- [ ] Optimize directories/files' owner/permissions in `knox_install_dir`
- [ ] Create Keystore and Truststore subdirectories
- [ ] Keystore and Trustore files with `knox_user` and `knox_group` permissions
- [ ] Reload systemd service (use handler daemon ?)
- [ ] Check webHDFS without Knox (enable Kerberos, SSL)
- [ ] Custom Knox (create topology for webHDFS via LDAP, complete with UI Hadoop, etc) ?
