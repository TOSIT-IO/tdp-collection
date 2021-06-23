# Ansible Spark TDP

This role deploys the Hive TDP release. It installs:

- Spark client
- Spark History Server

Currently the role only supports the deployment of SSL-enabled, Kerberos authenticated Spark History Server instances.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Hive TDP release .tar.gz (`spark_dist_file` role variable) file available in `files`
- Group `spark_hs` defined in the Ansible hosts file
- Role `ansible-hadoop` run on all `spark_hs` and `spark_client` nodes  as `hadoop_client`
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

## Example

The following hosts file and playbook are given as examples.

### Host file

```
[hadoop_client]
tdp-edge-1
tdp-spark-hs-1

[spark_client]
tdp-edge-1

[spark_hs]
tdp-spark-hs-1
```

### Playbook

```yaml
- name: "Deploy Spark"
  hosts: spark_client, spark_hs
  roles:
    - role: ansible-tdp/ansible-spark
      vars:
        realm: REALM.COM
        kadmin_principal: admin@REALM.COM
        kadmin_password: XXXXXXXX
        princ_password: p@ssw0rd123
        spark_defaults:
          spark.eventLog.dir: hdfs://mycluster/spark-logs
          spark.history.fs.logDirectory: hdfs://mycluster/spark-logs
          spark.yarn.historyServer.address: tdp-master-3.lxd:18081
```

## Post-installation tasks

Currently, the following post-installation must be run manually before starting all services:

```
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /spark-logs
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chown spark:hadoop /spark-logs
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chmod 777 /spark-logs
```

## Useful commands

### Run the Spark Pi example

```
export SPARK_CONF_DIR=/etc/spark/conf
/opt/tdp/spark/bin/spark-submit --class org.apache.spark.examples.SparkPi --master yarn --deploy-mode cluster /opt/tdp/spark/examples/jars/spark-examples_2.11-2.3.5-TDP-0.1.0-SNAPSHOT.jar 100
```

## TODO

- [ ] Secure the Spark History Server UI with SSL and Kerberos auth
