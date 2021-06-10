# Ansible TDP Collection

Ansible collection to deploy the components of TDP 

## Available Roles

- `hadoop`: deploys the Hadoop TDP Release (HDFS + YARN + MAPREDUCE)
- `hive`: deploys the Hive TDP Release (Hiveserver2 + Tez)
- `spark`: deploys the Spark TDP Release (Spark Client + Spark History Server)
- `ranger`: deploys the Ranger TDP Release (Ranger Admin)

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
│                   └── zookeeper
├── roles
├── test.yml

```
Note that the first `role` folder is **not** the roles from this collection, but any other roles the project has. The `collections` folder has been set in `ansible.cfg`.

### Ansible 2.10

Using ansible-galaxy: TBD

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
