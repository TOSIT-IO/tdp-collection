# Ansible Ranger TDP

This role deploys the Ranger TDP release. It installs:

- Ranger Admin
- Ranger Usersync
- Ranger Plugins

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

### Example playbooks

The [ranger.yml](../../playbooks/ranger.yml) playbook includes:
- Ranger Admin deployed with either:
  - PostgreSQL: [ranger_admin_postgresql.yml](../../playbooks/components/ranger_admin_postgresql.yml)
  - MySQL (default): [ranger_admin_mysql.yml](../../playbooks/components/ranger_admin_mysql.yml)
- Ranger Usersync using LDAP: [ranger_usersync.yml](../../playbooks/components/ranger_usersync.yml)
- Ranger Plugins (HDFS, YARN): [ranger_plugins.yml](../../playbooks/components/ranger_plugins.yml)


## TODO

- [ ] Automate the deployment of a minimal Solr installation to support audit logging
- [x] Automate the manual post-installations tasks
- [x] Create a Ranger Usersync subtask
- [ ] Fix Usersync with SSL Ranger Admin
- [ ] Automate the creation of the Ranger services in each plugin sub-tasks
  - [x] HDFS
  - [x] YARN
  - [ ] Hive
  - [ ] (?) Others
- [ ] (?) Automate the creation of the Ranger DB / DB user
- [x] Make the choice between MySQL / Postgres configurable
- [ ] Add handler to handle config changes (restart Admin and Usersync)
- [ ] Test Usersync with Unix sync and add example playbook
