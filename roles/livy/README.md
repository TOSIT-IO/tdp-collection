# Ansible Livy TDP

Deploys Apache Livy servers to the `livy_servers` Ansible group.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- `apache-livy-0.7.1-incubating-bin.zip` available in `files`
- Groups `livy_server` and `livy_client` defined in the Ansible inventory
- Certificate of the CA available as `root.pem` in `files`
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` available in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A functioning spark deployment and spark configuration files at SPARK_HOME of the `livy_server` hosts

## Example

The following hosts file and playbook are given as examples.

### Host file
```
[spark_client:children]
livy_server

[livy_server]
master-02
```

### Available Playbooks

- [livy.yml](../../playbooks/livy.yml):
  - A-Z deployment of Livy server

- [livy_user.yml](../../playbooks/livy_user.yml)
    - Setup the Livy user and their kerberos principal

- [livy_install.yml](../../playbooks/livy_install.yml):
  - Server setup and application deployment

- [livy_config.yml](../../playbooks/livy_config.yml)
  - Configuration of Livy service and Livy user setup

- [livy_server_start.yml](../../playbooks/livy_start.yml):
  - Starts Livy server

- [livy_server_stop.yml](../../playbooks/livy_stop.yml):
  - Stops Livy server

  ## TODO

  - Please check out the [Livy related issues](https://issues.apache.org/jira/projects/LIVY/issues/LIVY-795?filter=allopenissues).
