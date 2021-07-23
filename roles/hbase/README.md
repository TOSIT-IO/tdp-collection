# Ansible HBase TDP

This role deploys the HBase TDP release. It installs:

- HBase Master
- HBase RegionServer
- HBase Client

Currently the role only supports the deployment of SSL-enabled, Kerberos authenticated HBase clusters. HA is automatic when there is more than one HBase Master/

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- HBase TDP release .tar.gz (`hbase_dist_file` role variable) file available in `files`
- Groups `hbase_master`, `hbase_rs` defined in the Ansible hosts file
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

## Example

The following hosts file and playbook are given as examples.

### Host file

```
[hbase_master]
tdp-master-1
tdp-master-2

[hbase_rs]
tdp-worker-1
tdp-worker-2
tdp-worker-3

[hbase_client]
tdp-edge-1
```

### Required variables

- `realm`: Kerberos realm of the cluster
- `kadmin_principal`: admin principal used to connect kadmin service
- `kadmin_password`: passowrd of the admin principal

### Example playbooks

- [hbase.yml](../../playbooks/hbase.yml) deploys:
  - HBase Master
  - HBase RegionServers
  - HBase Client

## TODO

- [ ] Make the .tar.gz release file downloadable from a remote location
- [ ] Make a separate hbase_site for each services
- [x] Create a HBase client sub-task deploying everything needed for client side HBase
- [ ] Have hbase binaries available in the path in the HBase client sub-task
- [ ] Secure the HBase ZooKeeper znode (instructions [here](https://hbase.apache.org/book.html#_securing_zookeeper_data))
- [ ] (?) Make Kerberos auth optional
- [ ] (?) Make SSL optional
