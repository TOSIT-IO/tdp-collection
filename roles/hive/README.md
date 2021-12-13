# Ansible Hive TDP

This role deploys the Hive TDP release. It installs:

- HiveServer2

Currently the role only supports the deployment of SSL-enabled, Kerberos authenticated HiveServer2 instances. HA is automatic if there are more than one instances in the hosts file.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Hive TDP release .tar.gz (`hive_dist_file` role variable) file available in `files`
- Group `hive_s2` defined in the Ansible hosts file
- Role `hadoop` must have been previously executed on all `hive_s2` nodes as `hadoop_client`
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

## Example

The following hosts file and playbook are given as examples.

### Host file

```
[hadoop_client]
tdp-hive-s2-1
tdp-hive-s2-2

[hive_s2]
tdp-hive-s2-1
tdp-hive-s2-2
```

### Playbook

```yaml
- name: "Deploy Hive"
  hosts: hive_s2
  collections:
    - tosit.tdp
  roles:
    - role: hive
      vars:
        realm: REALM.COM
        kadmin_principal: admin@REALM.COM
        kadmin_password: XXXXXXXX
        hive_site:
          javax.jdo.option.ConnectionURL: jdbc:mysql://tdp-db-1.lxd:3306/hive
          hive.zookeeper.quorum: tdp-master-1.lxd:2181,tdp-master-2.lxd:2181,tdp-master-3.lxd:2181
          ranger_hive_install_properties:
            POLICY_MGR_URL: https://tdp-ranger-1.lxd:6182
            REPOSITORY_NAME: hive-mycluster
```

## Post-installation tasks

Currently, the following post-installation must be run manually before starting all services:

```
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /warehouse
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /warehouse/tablespace
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /warehouse/tablespace/managed
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /warehouse/tablespace/managed/hive
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chown hive:hadoop /warehouse/tablespace/managed/hive
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chmod 700 /warehouse/tablespace/managed/hive
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /warehouse/tablespace/external
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /warehouse/tablespace/external/hive
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chown hive:hadoop /warehouse/tablespace/external/hive
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chmod 777 /warehouse/tablespace/external/hive

/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /tmp/hive
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chown hive:hadoop /tmp/hive
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chmod 733 /tmp/hive

/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /tdp
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /tdp/tez
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -put /tmp/tez-0.9.1-TDP-0.1.0-SNAPSHOT.tar.gz /tdp/tez

/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /ranger/audit/hiveServer2
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chown hive:hive /ranger/audit/hiveServer2
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chmod 700 /ranger/audit/hiveServer2

systemctl start hiveserver2 (on all hs2)
```

## Useful commands

### Beeline

```
# Connect directly to a HS2 instance
/opt/tdp/hive/bin/hive --config /etc/hive/conf.s2 --service beeline -u "jdbc:hive2://tdp-hive-s2-2.lxd:10001/;principal=hive/_HOST@REALM.COM;transportMode=http;httpPath=cliservice;ssl=true;sslTrustStore=/etc/ssl/certs/truststore.jks;trustStorePassword=$pass"

# Connect through ZooKeeper
/opt/tdp/hive/bin/hive --config /etc/hive/conf.s2 --service beeline -u "jdbc:hive2://tdp-master-1.lxd:2181,tdp-master-2.lxd:2181,tdp-master-3.lxd:2181/;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=hiveserver2;sslTrustStore=/etc/ssl/certs/truststore.jks;trustStorePassword=$pass"

# Connect to a HS2 instance with the beeline alias
beeline -u "jdbc:hive2://tdp-hive-s2-2.lxd:10001/;principal=hive/_HOST@REALM.COM;transportMode=http;httpPath=cliservice;ssl=true;sslTrustStore=/etc/ssl/certs/truststore.jks;trustStorePassword=$pass"

# beeline_auto is another alias that connects directly through zk
beeline_auto
```

## TODO

- [ ] Secure the `javax.jdo.option.ConnectionPassword` and `javax.jdo.option.ConnectionUserName` hive-site.xml properties
- [ ] Improve the systemd service: make stdout, stderr and pid registration works
- [ ] Automate the manual post-installations tasks
- [ ] Create a Hive client sub-task deploying everything needed for client side Beeline sessions
- [ ] Create a Tez UI sub-task
- [ ] (?) Make a dedicated TDP Tez role
- [ ] (?) Make the choice between MySQL / Postgres configurable
