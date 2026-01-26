# Ansible HBase TDP

This is the main HBase directory. It includes the following sub-roles:

- HBase Master
- HBase RegionServer
- HBase REST
- HBase Client
- Phoenix Query Server
- Phoenix Client

Currently the roles only supports the deployment of SSL-enabled, Kerberos authenticated HBase clusters. HA is automatic when there is more than one HBase Master.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- HBase TDP release .tar.gz (`hbase_dist_file` role variable) file available in `files`
- Ranger TDP HBase plugin release .tar.gz (`ranger_hbase_dist_file` role variable) file available in `files`
- Phoenix TDP release .tar.gz (`phoenix_dist_file` role variable) file available in `files`
- Phoenix Query Server TDP release .tar.gz (`phoenix_queryserver_dist_file` role variable) file available in `files`
- Groups `hbase_master`, `hbase_rs`, `hbase_rest`, `hbase_client` defined in the Ansible inventory
- Groups `phoenix_queryserver_daemon`, `phoenix_queryserver_client` defined in the Ansible inventory
- Role `hadoop_client` must have been previously executed on all `hbase_rest` hosts
- Role `hadoop_client` must have been previously executed on all `phoenix_queryserver_daemon` hosts
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

## Example

The following hosts file and playbook are given as examples.

### Host file

```ini
[hbase_master]
tdp-master-1
tdp-master-2

[hbase_rs]
tdp-worker-1
tdp-worker-2
tdp-worker-3

[hbase_rest]
tdp-master-3

[hbase_client]
tdp-edge-1

[phoenix_queryserver_daemon]
master-03

[phoenix_queryserver_client]
edge-01
```

### Required variables

- `realm`: Kerberos realm of the cluster
- `kadmin_principal`: admin principal used to connect kadmin service
- `kadmin_password`: password of the admin principal

### Available playbooks

- [hbase.yml](../../playbooks/hbase.yml) deploys:
  - HBase Master
  - HBase RegionServers
  - HBase REST
  - HBase Client
  - Phoenix Query Server
  - Phoenix Query Server Client

- [ranger_plugins_hbase.yml](../../playbooks/ranger_plugins_hbase.yml) deploys:
  - Ranger HBase plugin

- [ranger_phoenix_policy.yml](../../playbooks/ranger_phoenix_policy.yml) deploys:
  - Ranger Phoenix policy

## TODO

Please check out the [HBase related issues](https://github.com/TOSIT-IO/ansible-tdp-roles/issues?q=is%3Aopen+is%3Aissue+label%3Ahbase).
