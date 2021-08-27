# TDP Architecture

TDP is a collection of ansible roles which deploy Hadoop big data services to your target machines. 

The hadoop component binaries are compiled directly from the open source repositories, meaning TDP hadoop deployments can be used commercially without cost.

This document is written as a high level technical overview for TDP project contributors, DBAs, sysadmins, data engineers etc. as an aid to understand how TDP deploys and configures Hadoop services. 

For a sandbox environment of a TDP cluster, the TDP getting started repo [add link here] deploys  a highly available Hadoop cluster on a virtual cluster on your local machine.

*All relative paths in this doc are relative to the appropriate `ansible.cfg` file used by TDP ansible roles.*

## TDP Repository structure

The project root largely contains links to *collection generic* resources (`docs/`, `.gitignore` etc.) and then the `roles/` directory:

- The `plugins/` directory includes the `access_fqdn` filter plugin definition, which is used frequently throughout the TDP ansible roles. TDP role agnostic tools and scripts belong here
- The `playbooks/` directory contains a suite of helper playbooks, including tests and example usage of the various TDP ansible roles. Ansible playbooks which use the TDP roles without changing them belong here 
- The `roles` directory is where the TDP roles are located. 1 directory/1 role per hadoop service. New hadoop component deployment roles belong here

  - *Some roles install multiple services if the dependency between them is mutual and specific (for example the `roles/Spark/` TDP role will install the *tez* service as well as the *spark* service. In such cases, both multiple binaries can be used in a single role*

### OS requirements
  - The TDP distribution uses `.tar.gz` format and have been tested on deployments to rhel7 and centos7 machines

### Software dependencies:

- ansible=2.9+ on the ansible host
- java-1.8.0-openjdk on all target nodes

### Network dependencies

- Network connectivity between all nodes
- Nodes must be able to resolve the fqdn of all other nodes

### Pre-deployment dependencies

- **Kerberos**

  - TDP currently requires the presence of a KDC and that appropriately configured kerberos-clients are available on each node in the cluster

  - A kerberos admin principal should exist before any deployment (the admin credentials and realm will be used to automate service principal creation)

  - A `krb5.conf` file with this KDC's information should be available on the ansible host at `files/krb5.conf` 

- **Certificate Authority**:

  - The files directory on the ansible host project root must contain CA public certificate at `files/root.pem`, and `files/<fqdn>.pem` `files/<fqdn>.key` key and signed certificate for each node in the cluster. 

### Hadoop component binary location

The binaries should be available in the the `files/` directory. 

### Ansible inventory file requirements

The ansible inventory file has 2 important roles in TDP:

1. As a source of truth for the node addresses
2. As mechanism to control to which servers the TDP roles deploy the hadoop services to.

These `domain` host variable should be present in the inventory file. The TDP `access_fqdn` plugin builds a fully qualified domain name dynamically from the ansible inventory file entries. It returns `access_fqdn`, or `access_sn` + `domain`, or `inventory_hostname` + `domain` (checking if variables exist for the host in this order).

The ansible inventory group names are:

- zk
- kdc
- hdfs_nn
- hdfs_jn
- hdfs_dn
- yarn_rm
- yarn_nm
- yarn_ats
- hive_s2
- hadoop_client
- ranger_admin

*In this extract of a TDP inventory file, the nodes are fully defined at the top then the ansible_hostnames are used to assign master-01, master-02 and master-03 as the zookeeper hosts and master-01 and master-02 as the hadoop namenodes:*

```
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

### Deployment order of TDP roles

Some of the TDP ansible roles rely on configuration files or clients deployed by other other TDP ansible roles. This creates a hard order of deployment in most cases. This order of deployment is outlined:

```
                                                +--------------+
                                                |              |
                                                |     +--------+------+
                        +-----------------------+-----+               |
                        |                       |     |   KDC         |
                        |              +--------+-----+               +-------------+
                        |              |        |     +-------+-------+             |
                        |              |        |             |                     |
                        |              |        |             |                     |
                        |              |        |     +-------v-------+             |
                        |              |        |     |               |             |
                        |              |        |     |   ZOOKEEPER   |             |
                        |              |        |     |          [TDP]|             |
                        |              |        |     +------+--------+             |
                        |              |        |            |                      |
                        |              |        |    +-------v--------+             |
+---------------+       |              |        |    |                |             |
|               |       |              |  +-----+----+    HADOOP      +----------+  |
|   DB INSTANCE |       |              |  |     |    |          [TDP] |          |  |
|               |       |              |  |     |    +-------+--------+          |  |
+---+---+-------+       |              |  |     +---+        |                   |  |
    |   |               |              |  |         |        |                   |  |
    |   |      +--------v-----+   +----v--v-------+ | +------v--------+   +------v--v-----+
    |   |      |              |   |               | | |               |   |               |
    |   +------>    HIVE      |   |    RANGER     | +>|   OOZIE       |   |     SPARK     |
    |          |         [TDP]|   |         [TDP] |   |          [TDP]|   |          [TDP]|
    |          +--------------+   +-------^-------+   +---------------+   +---------------+
    |                                     |
    |                                     |
    +-------------------------------------+
```

*Example - the order of TDP role execution for an oozie managed hdfs service would be:*

1. TDP Zookeeper role execution
2. TDP Hadoop role execution
3. TDP Oozie role execution

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
