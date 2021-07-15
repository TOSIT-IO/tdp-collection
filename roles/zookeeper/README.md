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
  hosts: zk
  tasks:
    - import_role:
        name: tosit.tdp.zookeeper
```

## Post-installation tasks


## TODO
- [x] Automate the post installation steps
- [x] Automate the creation of zk_server variables
