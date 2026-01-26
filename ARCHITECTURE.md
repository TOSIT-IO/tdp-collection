# TDP Architecture

TDP is a collection of ansible roles which deploy Hadoop-oriented big data services to your target machines. These Hadoop services are deployed with Hadoop component binaries, compiled directly from their open source repositories.

This document is written as a high level technical overview for TDP project contributors, DBAs, sysadmins, data engineers etc. as an aid to understand how TDP deploys and configures Hadoop services.

For a sandbox environment of a TDP cluster, the [TDP Getting Started](https://github.com/TOSIT-IO/tdp-getting-started) deploys a highly available Hadoop cluster on a virtual cluster on your local machine.

_All relative paths in this doc are relative to the appropriate `ansible.cfg` file used by TDP ansible roles._

## TDP Repository structure

The project root largely contains links to _collection generic_ resources (`docs/`, `.gitignore` etc.) and then the `roles/` directory:

- The `plugins/` directory includes the `access_fqdn` filter plugin definition, which is used frequently throughout the TDP ansible roles. TDP role agnostic tools and scripts belong here
- The `playbooks/` directory contains a suite of helper playbooks, including tests and example usage of the various TDP ansible roles. Ansible playbooks which use the TDP roles without changing them belong here
- The `roles` directory is where the TDP roles are located. 1 directory/1 role per Hadoop service. New Hadoop component deployment roles belong here

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
2. As mechanism to control to which servers the TDP roles deploy the Hadoop services to.

An example of an ansible inventory item definition is:

`worker-01 ansible_host=192.168.32.10 ansible_connection=ssh ansible_user=vagrant ip=192.168.32.10 domain=tdp`

The `domain` host variable must be present in the inventory file and the fqdn of the target should be `"{{inventory_hostname}}.{{domain}}"`. _Any deviation from this will break some default variable definitions (those which build the a node's fqdn based on the ansible inventory file using the TDP `access_fqdn` plugin._

The `ip` host variable must be present in the inventory file and should correspond to the IP address used within the cluster (it can deviate from the IP address used for Ansible administration). _Any deviation from this will break some tasks that rely on this variable._

Check the docs/DEVELOPER_DOCS.md file for more details and examples of the TDP distribution ansible inventory file.

### Deployment order of TDP roles

Some of the TDP ansible roles rely on configuration files or clients deployed by other other TDP ansible roles. This creates a hard order of deployment in most cases. This order of deployment is outlined:

```txt
                                                      +--------+------+
                        +-----------------------------+               |
                        |                             |   KDC         |
                        |              +--------------+               +-------------+
                        |              |              +-------+-------+             |
                        |              |                      |                     |
                        |              |                      |                     |
                        |              |              +-------v-------+             |
                        |              |              |               |             |
                        |              |              |   ZOOKEEPER   |             |
                        |              |              |          [TDP]|             |
                        |              |              +------+--------+             |
                        |              |                     |                      |
                        |              |             +-------v--------+             |
+---------------+       |              |             |                |             |
|               |       |              |  +----------+    HADOOP      +----------+  |
|   DB INSTANCE |       |              |  |          |          [TDP] |          |  |
|               |       |              |  |          +-------+--------+          |  |
+---+---+-------+       |              |  |                                      |  |
    |   |               |              |  |                                      |  |
    |   |      +--------v-----+   +----v--v-------+                       +------v--v-----+
    |   |      |              |   |               |                       |               |
    |   +------>    HIVE      |   |    RANGER     |                       |     SPARK     |
    |          |         [TDP]|   |         [TDP] |                       |          [TDP]|
    |          +--------------+   +-------^-------+                       +---------------+
    |                                     |
    |                                     |
    +-------------------------------------+
```

_Example - the order of TDP role execution for an oozie managed hdfs service would be:_

1. TDP Zookeeper role execution
2. TDP Hadoop role execution
3. TDP Oozie role execution
