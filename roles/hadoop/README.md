# Ansible Hadoop TDP

This is the main Hadoop directory. It includes the following sub-roles:

- HDFS Namenode + HDFS ZKFC
- HDFS Datanode
- YARN ResourceManager
- YARN NodeManager
- YARN Application Timeline Service
- Hadoop Client

Currently the roles only supports the deployment of HA, SSL-enabled, Kerberos authenticated Hadoop clusters.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Hadoop TDP release .tar.gz (`hadoop_dist_file` role variable) file available in `files`
- Ranger TDP Hadoop plugin release .tar.gz (`ranger_hdfs_dist_file` role variable) file available in `files`
- Groups `hdfs_nn`, `hdfs_jn`, `hdfs_dn`, `yarn_rm`, `yarn_nm`, `hadoop_client` defined in the Ansible inventory
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

## Example

The following hosts file and playbook are given as examples.

### Host file

```
[hdfs_nn]
tdp-master-1
tdp-master-2

[hdfs_jn]
tdp-master-1
tdp-master-2
tdp-master-3

[hdfs_dn]
tdp-worker-1
tdp-worker-2
tdp-worker-3

[yarn_rm]
tdp-master-1
tdp-master-2

[yarn_nm]
tdp-worker-1
tdp-worker-2
tdp-worker-3

[yarn_ats]
tdp-master-3

[hadoop_client]
tdp-edge-1
```

### Available playbooks

- [hadoop.yml](../../playbooks/hadoop.yml) deploys:
  - HDFS Namenodes
  - HDFS Datanodes
  - HDFS Journalnodes
  - YARN Resource Managers
  - YARN Node Managers

- [ranger_plugins_hadoop.yml](../../playbooks/ranger_plugins_hadoop.yml) deploys:
  - Ranger HDFS plugin
  - Ranger YARN plugin

## Advenced Configuration

- For better integration and in order to resolve the resiliency issue of Yarn Timeline Server, we recommend setting these specific parameters:
  - yarn-site.xml
    - yarn.timeline-service.client.best-effort: true
    - yarn.timeline-service.client.max-retries: 3


## TODO

Please check out the [Hadoop related issues](https://github.com/TOSIT-FR/ansible-tdp-roles/issues?q=is%3Aissue+is%3Aopen+label%3Ahadoop).
