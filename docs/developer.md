# Developer Documentation

This document is targeted at new TDP distribution contributors and covers in some detail topics related to the configuration and extension of the TDP distribution project.

## Ansible inventory file requirements

The ansible inventory file has 2 important roles in TDP:

1. As a source of truth for the node addresses
2. As mechanism to control to which servers the TDP roles deploy the services to.

The `domain` host variable should be present in the inventory file. The TDP `access_fqdn` plugin builds a fully qualified domain name dynamically from the ansible inventory file entries. It returns `access_fqdn`, or `access_sn` + `domain`, or `inventory_hostname` + `domain` (checking if variables exist for the host in this order).

The ansible inventory group names are:

- zk
- hdfs_nn
- hdfs_jn
- hdfs_dn
- yarn_rm
- yarn_nm
- yarn_ats
- hadoop_client
- hive_s2
- hive_client
- hbase_master
- hbase_rs
- hbase_client
- phoenix_queryserver_daemon
- phoenix_queryserver_client
- knox
- ranger_admin
- ranger_usersync

*In this extract of a TDP inventory file, the nodes are fully defined at the top then the ansible_hostnames are used to assign master-01, master-02 and master-03 as the zookeeper hosts and master-01 and master-02 as the Hadoop namenodes:*

```ini
[all]
worker-01 ansible_host=192.168.32.10 ansible_connection=ssh ansible_user=vagrant domain=tdp
worker-02 ansible_host=192.168.32.11 ansible_connection=ssh ansible_user=vagrant domain=tdp
worker-03 ansible_host=192.168.32.12 ansible_connection=ssh ansible_user=vagrant domain=tdp
master-01 ansible_host=192.168.32.13 ansible_connection=ssh ansible_user=vagrant domain=tdp
master-02 ansible_host=192.168.32.14 ansible_connection=ssh ansible_user=vagrant domain=tdp
master-03 ansible_host=192.168.32.15 ansible_connection=ssh ansible_user=vagrant domain=tdp
edge-01 ansible_host=192.168.32.16 ansible_connection=ssh ansible_user=vagrant domain=tdp
edge-02 ansible_host=192.168.32.17 ansible_connection=ssh ansible_user=vagrant domain=tdp

[zk]
master-01
master-02
master-03

[hdfs_nn]
master-01
master-02
```

Use the access_fqdn plugin to generate the fqdn of from the inventory_hostname and the domain e.g. `"{{ groups[hdfs_nn][0] | access_fqdn(hostvars) }}"` would evaluate to `master-01.tdp`.

## TDP Service Configuration

Each TDP role includes a `tdp/roles/<TDP-role>/defaults/main.yaml` file including a set of reasonable defaults. These defaults take the form of:

- key:value pairs
- yaml hashes
- jinja templating language blocks to generate values e.g. processing the ansible inventory file using the access_fqdn plugin

These default variables are **scoped to their own role** meaning that the editing the value in one role won't impact other TDP roles deployment. However, some traps to avoid are:

**Ansible variable precedence behaviour**
The scoping and precedence of variables in ansible is already well documented [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html) and should be the first port of call in case of unexpected behaviour related to variable values.

**Node address changes**

Optimally, **any node address changes should be made in the ansible inventory file**, as some defaults build node addresses values dynamically using the ansible inventory file. This means that any node address changes outside of the ansible inventory files (such as hardcoding the hadoop_ha_zookeeper_quorum string in `tdp/roles/hadoop/defaults/main.yaml`) may create a misalignment with other TDP roles (e.g. `tdp/roles/zookeeper/defaults/main.yml`) which dynamically generate the quorum address based on the inventory file.

**Partially overiding hashes**

In ansible, partially updating a hash is not possible without deviating from the default ansible configuration

By default, given the below hash:

```yaml
hdfs_site:
  dfs.replication: 1
  dfs.nameservices: mycluster
  dfs.ha.namenodes.mycluster: nn1,nn2
```

...the following attempted update to hdfs_site.dfs.replication:

```yaml
hdfs_site:
  dfs.replication: 1
```

... will replace `hdfs_site` completely, removing `dfs.nameservices` and `dfs.ha.namenodes.mycluster` from the `hdfs_site` hash.

To enable the **merging** of an overridden value in to an existing hash (only updating the differences), add the following to the `ansible.cfg` file for your deployment:

```yaml
# Default behavior
# hash_behaviour = replace

# To enable partial hash updates
hash_behaviour = merge
```

See [here](https://docs.ansible.com/ansible/2.4/intro_configuration.html#id112) for the ansible docs regarding this.
