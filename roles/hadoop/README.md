# Ansible Hadoop TDP

This role deploys the Hadoop TDP release. It installs:

- HDFS Namenode + HDFS ZKFC
- HDFS Datanode
- YARN ResourceManager
- YARN NodeManager

Currently the role only supports the deployment of HA, SSL-enabled, Kerberos authenticated Hadoop clusters.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Hadoop TDP release .tar.gz (`hadoop_dist_file` role variable) file available in `files`
- Groups `hdfs_nn`, `hdfs_jn`, `hdfs_dn`, `yarn_rm`, `yarn_nm`, `hadoop_client` defined in the Ansible hosts file
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

[hadoop_client]
tdp-edge-1
```

### Required variables

- `realm`: Kerberos realm of the cluster
- `kadmin_principal`: admin principal used to connect kadmin service
- `kadmin_password`: passowrd of the admin principal

### Example playbooks

- [hadoop.yml](../../playbooks/hadoop.yml) deploys:
  - HDFS Namenodes
  - HDFS Datanodes
  - HDFS Journalnodes
  - YARN Resource Managers
  - YARN Node Managers

## TODO

- [ ] Create a YARN Timeline Server sub-task
- [ ] Create a YARN Timeline Service v2 sub-task (once we have HBase)
- [ ] Create a MapReduce JobHistory sub-task
- [ ] Make the .tar.gz release file downloadable from a remote location
- [ ] Make a separate hdfs_site / yarn_site for each services
- [x] Create a Hadoop client sub-task deploying everything needed for client side HDFS / YARN
- [ ] Have hdfs/hadoop/yarn binaries available in the path in the Hadoop client sub-task
- [x] Automate the manual post-installations tasks
- [ ] Secure the HA ZooKeeper znode (instructions [here](https://hadoop.apache.org/docs/r3.1.1/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html#Securing_access_to_ZooKeeper))
- [ ] (?) Make Kerberos auth optional
- [ ] (?) Make SSL optional
- [ ] (?) Make HA optional
