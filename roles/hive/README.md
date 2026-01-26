# Ansible Hive TDP

This is the main Hive directory. It includes the following sub-roles:

- HiveServer2
- Hive Client
- Tez

Currently the role only supports the deployment of SSL-enabled, Kerberos authenticated HiveServer2 instances. HA is automatic if there are more than one instances in the hosts file.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Hive TDP release .tar.gz (`hive_dist_file` role variable) file available in `files`
- Ranger TDP Hive plugin release .tar.gz (`ranger_hive_dist_file` role variable) file available in `files`
- Tez TDP release .tar.gz (`tez_dist_file` role variable) file available in `files`
- Groups `hive_s2` and `hive_client` defined in the Ansible inventory
- Role `hadoop_client` must have been previously executed on all `hive_s2` hosts
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

## Example

The following hosts file and playbook are given as examples.

### Host file

```ini
[hive_s2]
tdp-master-2
tdp-master-3

[hive_client]
tdp-edge-1
```

### Available Playbooks

- [hive.yml](../../playbooks/hive.yml) deploys:
  - HiveServer2
  - Tez

- [ranger_plugins_hive.yml](../../playbooks/ranger_plugins_hive.yml) deploys:
  - Ranger Hive plugin

## Useful commands

### Beeline

```sh
# Connect directly to a HS2 instance
/opt/tdp/hive/bin/hive --config /etc/hive/conf.s2 --service beeline -u "jdbc:hive2://tdp-hive-s2-2.lxd:10001/;principal=hive/_HOST@REALM.COM;transportMode=http;httpPath=cliservice;ssl=true;sslTrustStore=/etc/ssl/certs/truststore.jks;trustStorePassword=$pass"

# Connect through ZooKeeper
/opt/tdp/hive/bin/hive --config /etc/hive/conf.s2 --service beeline -u "jdbc:hive2://tdp-master-1.lxd:2181,tdp-master-2.lxd:2181,tdp-master-3.lxd:2181/;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=hiveserver2;sslTrustStore=/etc/ssl/certs/truststore.jks;trustStorePassword=$pass"

# beeline is an alias that connects directly through zk
beeline
```

## TODO

Please check out the [Hive related issues](https://github.com/TOSIT-IO/ansible-tdp-roles/issues?q=is%3Aopen+is%3Aissue+label%3Ahive).
