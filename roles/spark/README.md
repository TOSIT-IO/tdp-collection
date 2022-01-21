# Ansible Spark TDP

This is the main Spark directory. It includes the following sub-roles:

- Spark client
- Spark History Server

Currently the role only supports the deployment of SSL-enabled, Kerberos authenticated Spark History Server instances.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Spark TDP release .tar.gz (`spark_dist_file` role variable) file available in `files`
- Group `spark_hs` and `spark_client` defined in the Ansible inventory
- Role `hadoop_client` must have been previously executed on all `spark_hs` and `spark_client` hosts
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

## Example

The following hosts file and playbook are given as examples.

### Host file

```
[spark_client]
tdp-edge-1

[spark_hs]
tdp-master-3
```

### Available Playbooks

- [spark.yml](../../playbooks/spark.yml) deploys:
  - Spark client
  - Spark History Server

## Useful commands

### Run the Spark Pi example

```
export SPARK_CONF_DIR=/etc/spark/conf
/opt/tdp/spark/bin/spark-submit --class org.apache.spark.examples.SparkPi --master yarn --deploy-mode cluster /opt/tdp/spark/examples/jars/spark-examples_2.11-2.3.5-TDP-0.1.0-SNAPSHOT.jar 100
```

### Start a Spark Shell in client mode

```
export SPARK_CONF_DIR=/etc/spark/conf
/opt/tdp/spark/bin/spark-shell --master yarn --deploy-mode client
```

## TODO

Please check out the [Spark related issues](https://github.com/TOSIT-FR/ansible-tdp-roles/issues?q=is%3Aopen+is%3Aissue+label%3Aspark).
