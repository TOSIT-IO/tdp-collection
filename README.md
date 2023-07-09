# Ansible TDP Collection

Ansible collection to deploy the components of TDP

## Available Roles

- `hadoop`: deploys the [Hadoop](https://github.com/TOSIT-FR/hadoop) TDP Release (HDFS + YARN + MapReduce)
- `hbase`: deploys the [HBase](https://github.com/TOSIT-FR/hbase) TDP Release (HBase Master + HBase RegionServer), [Phoenix](https://github.com/TOSIT-FR/phoenix) and [Phoenix Query Server](https://github.com/TOSIT-FR/phoenix-queryserver)
- `hive`: deploys the [Hive](https://github.com/TOSIT-FR/hive) TDP Release (Hiveserver2 + Tez)
- `knox`: deploys the [Knox](https://github.com/TOSIT-FR/Knox) TDP Release (Knox Gateway)
- `ranger`: deploys the [Ranger](https://github.com/TOSIT-FR/ranger) TDP Release (Ranger Admin + Ranger plugins)
- `spark`: deploys the [Spark](https://github.com/TOSIT-FR/spark) TDP Release (Spark Client + Spark History Server)
- `zookeeper`: deploys the Apache ZooKeeper Release

## Getting started

The best to get started with TDP and the Ansible roles is to go through the [Getting Started](https://github.com/TOSIT-IO/tdp-getting-started) repository.

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

#### Mitogen 0.2

The collection is compatible with [Mitogen](https://mitogen.networkgenomics.com/ansible_detailed.html) 0.2.

In order to activate Mitogen, follow the [Mitogen installation guide](https://mitogen.networkgenomics.com/ansible_detailed.html#installation).

*Note:* We use [custom plugins](https://github.com/TOSIT-IO/tdp-collection/tree/master/plugins) which are incompatible with Mitogen. For this reason, we added `strategy: linear` in some of our playbooks (e.g.: [hbase_hdfs_init.yml](https://github.com/TOSIT-IO/tdp-collection/blob/master/playbooks/hbase_hdfs_init.yml)) to avoid any issues with Mitogen configured Ansible environments.

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

The best way to use the roles from the collection is to call the related file from the `playbooks` directory inside another playbook.

Examples:
```
- name: Deploy ZooKeeper
  ansible.builtin.import_playbook: ansible_roles/collections/ansible_collections/tosit/tdp/playbooks/zookeeper.yml

- name: Deploy Hadoop
  ansible.builtin.import_playbook: ansible_roles/collections/ansible_collections/tosit/tdp/playbooks/hadoop.yml

- name: Deploy Hive
  ansible.builtin.import_playbook: ansible_roles/collections/ansible_collections/tosit/tdp/playbooks/hive.yml
```

## Contribute

### Dev dependencies

- Python >= 3.6 with virtual env package (i.e. `python3-venv`)

Please follow the guidelines at [contributing](./docs/contributing.md) and respect the [code of conduct](./CODE_OF_CONDUCT.md).
