# Ansible Hadoop TDP

This is the main ZooKeeper directory. It includes the following sub-roles:

- ZooKeeper server
- ZooKeeper client

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- ZooKeeper .tar.gz (`zookeeper_dist_file` role variable) file available in `files`
- Group `zk` defined in the Ansible inventory
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

### Host file

```ini
[zk]
tdp-master-1
tdp-master-2
tdp-master-3

[zk_client:children]
edge
```

### Available Playbooks

- [zookeeper.yml](../../playbooks/zookeeper.yml) deploys:
  - ZooKeeper Server
  - ZooKeeper Client

## TODO

Please check out the [ZooKeeper related issues](https://github.com/TOSIT-IO/ansible-tdp-roles/issues?q=is%3Aopen+is%3Aissue+label%3Azookeeper).
