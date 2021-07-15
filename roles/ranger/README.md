# Ansible Ranger TDP

This role deploys the Ranger TDP release. It installs:

- Ranger Admin
- Ranger Usersync

Currently the role only supports the deployment of SSL-enabled, Kerberos authenticated Ranger Admin instances.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Ranger TDP release .tar.gz (`ranger_dist_file` role variable) file available in `files`
- Group `ranger_admin` defined in the Ansible hosts file
- Role `hadoop` must have been previously executed on all `ranger_admin` node as `hadoop_client`
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

## Example

The following hosts file and playbook are given as examples.

### Host file

```
[hadoop_client]
tdp-ranger-1

[ranger_admin]
tdp-ranger-1
```

### Playbook

#### Ranger Admin

```yaml
- name: "Deploy Ranger"
  roles:
    - role: tosit.tdp.ranger
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

#### Ranger Usersync

```yaml
- name: "Deploy Ranger Usersync"
  hosts: ranger_admin
  tasks:
    - import_role:
        name: tosit.tdp.ranger
        tasks_from: ranger_usersync
      vars:
        usersync_install_properties:
          SYNC_LDAP_BIND_DN: cn=example,c=fr
          SYNC_LDAP_BIND_PASSWORD: XXXXXXX
```

## Post-installation tasks

Currently, the following post-installation must be run manually:

```
systemctl start ranger-admin
```

## TODO

- [ ] Automate the deployment of a minimal Solr installation to support audit logging
- [ ] Automate the manual post-installations tasks
- [x] Create a Ranger Usersync subtask
- [ ] Fix Usersync with SSL Ranger Admin
- [ ] Automate the creation of the Ranger services in each plugin sub-tasks
- [ ] (?) Automate the creation of the Ranger DB / DB user
- [x] Make the choice between MySQL / Postgres configurable
- [ ] Add handler to handle config changes (restart Admin and Usersync)
