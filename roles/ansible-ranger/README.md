# Ansible Ranger TDP

This role deploys the Ranger TDP release. It installs:

- Ranger Admin

Currently the role only supports the deployment of SSL-enabled, Kerberos authenticated Ranger Admin instances.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Ranger TDP release .tar.gz (`ranger_dist_file` role variable) file available in `files`
- Group `ranger_admin` defined in the Ansible hosts file
- Role `ansible-hadoop` run on `ranger_admin` node as `hadoop_client`
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

## Example

The following hosts file and playbook are given as examples.

### Host file

```
[ranger_admin]
tdp-ranger-1 ansible_ssh_port=30004 ansible_ssh_host=noeyyazu.noe.edf.fr
```

### Playbook

```yaml
- name: "Deploy Ranger"
  hosts: ranger_admin
  roles:
    - role: ansible-tdp/ansible-ranger
      vars:
        realm: REALM.COM
        kadmin_principal: admin@REALM.COM
        kadmin_password: XXXXXXXX
        princ_password: p@ssw0rd123
        install_properties:
          db_host: tdp-db-1.lxd:3306
          db_user: ranger
          db_password: ranger123
```

## Post-installation tasks

Currently, the following post-installation must be run manually before starting all services:

```
systemctl start ranger-admin
```

## TODO

- [ ] Automate the deployment of a minimal Solr installation to support audit logging
- [ ] Make the choice between MySQL / Postgres configurable
- [ ] Automate the manual post-installations tasks
- [ ] Create a Ranger Usersync subtask
- [ ] (?) Automate the creation of the Ranger DB / DB user
