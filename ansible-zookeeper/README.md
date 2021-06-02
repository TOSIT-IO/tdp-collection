# Ansible Hadoop TDP

This role deploys the Zookeeper release. It installs:

- Zookeeper server


## Prerequisites

### Host file

```
[zk:children]
master1
master2
master3
```

### Playbook

```yaml
- name: "Deploy Zookeeper"
  hosts: all
  roles:
    - role: github-roles/ansible-zookeeper
      vars:
        zk_server_01: chung-master-01.novalocal:2888:3888
        zk_server_02: chung-master-02.novalocal:2888:3888
        zk_server_03: chung-master-03.novalocal:2888:3888
```

## Post-installation tasks

Currently, the following post-installation must be run manually before starting all services:

```
Create myid file on /opt/tdp/zookeeper/zkData directory of each Zookeeper server.myid contains the id of each server which is used for election.
bin/zkServer.sh start
```

## TODO
