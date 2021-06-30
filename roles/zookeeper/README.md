# Ansible Hadoop TDP

This role deploys the Zookeeper release. It installs:

- Zookeeper server

## Prerequisites
- Zookeeper .tar.gz (`zookeeper_dist_file` role variable) file available in `files`

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


## TODO
- Automate the post installation steps - DONE
- Automate the creation of zk_server variables
