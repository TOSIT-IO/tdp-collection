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
- Groups `hdfs_nn`, `hdfs_jn`, `hdfs_dn`, `yarn_rm`, `yarn_nm` defined in the Ansible hosts file
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
```

### Playbook

```yaml
- name: "Deploy Hadoop"
  hosts: all
  roles:
    - role: ansible-tdp/ansible-hadoop
      vars:
        hadoop_ha_zookeeper_quorum: tdp-master-1.lxd:2181,tdp-master-2.lxd:2181,tdp-master-3.lxd:2181
        hadoop_dfs_namenode_rpc_adress_mycluster_nn1: tdp-master-1.lxd:8020
        hadoop_dfs_namenode_rpc_adress_mycluster_nn2: tdp-master-2.lxd:8020
        hadoop_dfs_namenode_http_adress_mycluster_nn1: tdp-master-1.lxd:9870
        hadoop_dfs_namenode_http_adress_mycluster_nn2: tdp-master-2.lxd:9870
        hadoop_dfs_namenode_https_adress_mycluster_nn1: tdp-master-1.lxd:9871
        hadoop_dfs_namenode_https_adress_mycluster_nn2: tdp-master-2.lxd:9871
        hadoop_dfs_namenode_shared_edits_dir: qjournal://tdp-master-1.lxd:8485;tdp-master-2.lxd:8485;tdp-master-3.lxd:8485/mycluster
        realm: REALM.COM
        kadmin_principal: admin@REALM.COM
        kadmin_password: XXXXXXXX
        princ_password: p@ssw0rd123
        yarn_resourcemanager_hostname_rm1: tdp-master-1.lxd
        yarn_resourcemanager_hostname_rm2: tdp-master-2.lxd
        yarn_resourcemanager_webapp_address_rm1: tdp-master-1.lxd:8088
        yarn_resourcemanager_webapp_address_rm2: tdp-master-2.lxd:8088
        yarn_resourcemanager_webapp_https_address_rm1: tdp-master-1.lxd:8090
        yarn_resourcemanager_webapp_https_address_rm2: tdp-master-2.lxd:8090
```

## Post-installation tasks

Currently, the following post-installation must be run manually before starting all services:

```
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf.nn zkfc -formatZK (on a nn)
systemctl start hadoop-hdfs-journalnode (on all 3 jn)
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf.nn namenode -format (on one nn)
systemctl start hadoop-hdfs-namenode (on one nn)
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf.nn namenode -bootstrapStandby (on the other nn)
systemctl start hadoop-hdfs-namenode (on the other nn)
systemctl start hadoop-hdfs-zkfc (on both nn)

systemctl start hadoop-yarn-resourcemanager (on both rm)
systemctl start hadoop-yarn-nodemanager (on all nm)
```

```
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /mr-history
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chmod 777 /mr-history
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chown mapred:hadoop /mr-history
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /mr-history/done
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /mr-history/tmp
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chmod 777 /mr-history/tmp
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chmod 777 /mr-history/done
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chown mapred:hadoop /mr-history/tmp
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chown mapred:hadoop /mr-history/done

/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -mkdir /app-logs
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chmod 777 /app-logs
/opt/tdp/hadoop/bin/hdfs --config /etc/hadoop/conf dfs -chown yarn:hadoop /app-logs
```

## TODO

- [ ] Create a YARN Timeline Service v2 sub-task
- [ ] Create a MapReduce JobHistory sub-task
- [ ] Make the .tar.gz release file downloadable from a remote location
- [ ] Split the hdfs_site and yarn_site vars for each services
- [x] Create a Hadoop client sub-task deploying everything needed for client side HDFS / YARN
- [ ] Automate the manual post-installations tasks
- [ ] Secure the HA ZooKeeper znode (instructions [here](https://hadoop.apache.org/docs/r3.1.1/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html#Securing_access_to_ZooKeeper))
- [ ] (?) Make Kerberos auth optional
- [ ] (?) Make SSL optional
- [ ] (?) Make HA optional
