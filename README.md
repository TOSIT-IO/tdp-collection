# Ansible TDP Collection

Ansible collection to deploy the components of TDP

## Available Roles

- `zookeeper`: deploys the Apache ZooKeeper Release
- `hadoop`: deploys the [Hadoop](https://github.com/TOSIT-FR/hadoop) TDP Release (HDFS + YARN + MapReduce)
- `hive`: deploys the [Hive](https://github.com/TOSIT-FR/hive) TDP Release (Hiveserver2 + Tez)
- `spark`: deploys the [Spark](https://github.com/TOSIT-FR/spark) TDP Release (Spark Client + Spark History Server)
- `ranger`: deploys the [Ranger](https://github.com/TOSIT-FR/ranger) TDP Release (Ranger Admin + Ranger plugins)
- `oozie`: deploys the [Oozie](https://github.com/TOSIT-FR/oozie) TDP Release (Oozie Server)
- `hbase`: deploys the [HBase](https://github.com/TOSIT-FR/hbase) TDP Release (HBase Master + HBase RegionServer)
- `knox`: deploys the [Knox](https://github.com/TOSIT-FR/Knox) TDP Release (Knox Gateway)

## Getting started

The best to get started with TDP and the Ansible roles is to go through the [Getting Started](https://github.com/TOSIT-FR/getting-started) repository.

## Install the collection

### Ansible 2.9

Ansible 2.9 does not handle installing a collection from a Git repository with `ansible-galaxy`. Instead, clone the repository in the correct folder.

For example, set the property `collections_paths` in your `ansible.cfg`:

```ini
[defaults]
collections_paths=collections
```

Then create the folders structures and clone:
```
mkdir -p collections/ansible_collections/tosit
git clone https://github.com/TOSIT-FR/ansible-tdp-roles collections/ansible_collections/tosit/tdp
```

The project structure should look like this:

```
.
├── ansible.cfg
├── collections
│   └── ansible_collections
│       └── tosit
│           └── tdp
│               ├── galaxy.yml
│               ├── README.md
│               └── roles
│                   ├── hadoop
│                   ├── hive
│                   ├── ranger
│                   ├── spark
│                   ├── ...
│                   └── zookeeper
├── roles
├── test.yml
```

Note that the first `role` folder is **not** the roles from this collection, but any other roles the project has. The `collections` folder has been set in `ansible.cfg`.

### Ansible 2.10

Using ansible-galaxy: TBD

## Plugins and modules


- `hdfs_file` module: file and directory handling in HDFS

Example usage:
```yml
- name: Add directory for spark logs
  delegate_to: "{{ groups['hdfs_nn'][0] }}"
  tosit.tdp.hdfs_file:
    hdfs_conf: "{{ hadoop_conf_dir }}"
    path: "{{ item.path }}"
    state: "{{ item.state | default(omit) }}"
    owner: "{{ item.owner | default(omit) }}"
    group: "{{ item.group | default(omit) }}"
    mode: "{{ item.mode | default(omit) }}"
  become: yes
  become_user: "{{ hdfs_user }}"
  loop:
    - path: /spark-logs
      state: directory
      owner: "{{ spark_user }}"
      group: "{{ hadoop_group }}"
      mode: '777'
```

- `access_fqdn` filter plugin: returns `access_fqdn`, or `access_sn` + `domain`, or `inventory_hostname` + `domain` (checking if variables exist for the host in this order)

Example usage:
```yml
- debug:
    msg: "{{ groups[hdfs_nn][0] | access_fqdn(hostvars) }}"

- debug:
    msg: "{{ groups['hdfs_jn'] | map('access_fqdn', hostvars) | list }}"
```

## Use a role from the collection

Example:
```
- hosts: all
  tasks:
    - import_role:
        name: tosit.tdp.hadoop
```

To avoid repeating namespace `tosit.tdp`:
```
- hosts: localhost
  collections:
    - tosit.tdp
  tasks:
    - import_role:
        name: hadoop

```

## Contribute

Please follow the guidelines at [contributing](./docs/contributing.md) and respect the [code of conduct](./CODE_OF_CONDUCT.md).

## Contributors

- [leopaul36](https://github.com/leopaul36)
- [RReivax](https://github.com/RReivax)
- [rpignolet](https://github.com/rpignolet)
- [Guillaume-Boutry](https://github.com/Guillaume-Boutry)
- [nschung](https://github.com/nschung)
