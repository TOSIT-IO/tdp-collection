# Ansible Ranger TDP

This is the main Ranger directory. It includes the following sub-roles:

- Ranger Admin
- Ranger Usersync
- Ranger Plugins

Currently the role only supports the deployment of SSL-enabled, Kerberos authenticated Ranger Admin instances.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Ranger TDP release .tar.gz (`ranger_dist_file` role variable) file available in `files`
- Groups `ranger_admin` and `ranger_usersync` defined in the Ansible inventory
- Role `hadoop_client` must have been previously executed on all `ranger_admin` hosts
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

## Example

The following hosts file and playbook are given as examples.

### Host file

```
[ranger_admin]
tdp-master-3

[ranger_usersync]
tdp-master-3
```

### Available Playbooks

- [ranger.yml](../../playbooks/ranger.yml) deploys:
  - Ranger Admin deployed with either:
    - PostgreSQL: [ranger_admin_postgresql.yml](../../playbooks/components/ranger_admin_postgresql.yml)
    - MySQL (default): [ranger_admin_mysql.yml](../../playbooks/components/ranger_admin_mysql.yml)
  - Ranger Usersync using LDAP: [ranger_usersync.yml](../../playbooks/components/ranger_usersync.yml)

## TODO

Please check out the [Ranger related issues](https://github.com/TOSIT-FR/ansible-tdp-roles/issues?q=is%3Aopen+is%3Aissue+label%3Aranger).
