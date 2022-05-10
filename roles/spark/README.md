# Ansible Spark TDP

This is the main Spark directory. It includes the following sub-roles:

- Spark client
- Spark History Server

Currently the role only supports the deployment of SSL-enabled, Kerberos authenticated Spark History Server instances.

This role can be used to install both Spark 2 and Spark 3.

## Prerequisites

For all Spark versions:

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Spark TDP release .tar.gz (`spark_dist_file` role variable) file available in `files`
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

For Spark 2:

- Groups `spark_hs` and `spark_client` defined in the Ansible inventory
- Role `hadoop_client` must have been previously executed on all `spark_hs` and `spark_client` hosts

For Spark 3:

- `python3.6+` installed on `spark3_client` and worker (=`yarn_nm`) nodes
- `py4j>=0.10.9.3` PyPI package installed for Python 3 on `spark3_client` and worker (=`yarn_nm`) nodes
- Groups `spark3_hs` and `spark3_client` defined in the Ansible inventory
- Role `hadoop_client` must have been previously executed on all `spark3_hs` and `spark3_client` hosts

(Optional) For pandas API on Spark 3:

- `python3-pip` and `python3-setuptools` installed on `spark3_client` and worker (=`yarn_nm`) nodes
- `numpy>=1.14`, `pandas>=0.23.2`, `pyarrow>=1.0.0` PyPI package installed for Python 3 on `spark3_client` and worker (=`yarn_nm`) nodes

## Example

The following hosts file and playbook are given as examples.

### Host file

```
[spark_client]
tdp-edge-1

[spark_hs]
tdp-master-3

[spark3_client]
tdp-edge-1

[spark3_hs]
tdp-master-3
```

### Available Playbooks

- [spark.yml](../../playbooks/spark.yml) deploys:

  - Spark client
  - Spark History Server

- [spark3.yml](../../playbooks/spark3.yml) deploys:
  - Spark 3 client
  - Spark 3 History Server

## Useful commands

### Run the Spark Pi example

```bash
# Spark 2
export SPARK_CONF_DIR=/etc/spark/conf
spark-submit --class org.apache.spark.examples.SparkPi --master yarn --deploy-mode cluster /opt/tdp/spark/examples/jars/spark-examples_2.11-2.3.5-TDP-0.1.0-SNAPSHOT.jar 100

# Spark 3
export SPARK_CONF_DIR=/etc/spark3/conf
spark3-submit --class org.apache.spark.examples.SparkPi --master yarn --deploy-mode cluster /opt/tdp/spark3/examples/jars/spark-examples_2.12-3.2.2-TDP-0.1.0-SNAPSHOT.jar 100
```

### Start a Spark Shell in client mode

```bash
# Spark 2
export SPARK_CONF_DIR=/etc/spark/conf
spark-shell --master yarn --deploy-mode client

# Spark 3
export SPARK_CONF_DIR=/etc/spark3/conf
spark3-shell --master yarn --deploy-mode client
```

## TODO

Please check out the [Spark related issues](https://github.com/TOSIT-FR/ansible-tdp-roles/issues?q=is%3Aopen+is%3Aissue+label%3Aspark).
