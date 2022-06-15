# Ansible Kafka TDP

This is the main Kafka directory. It includes the following sub-roles:

- Kafka Broker
- Kafka Client

Currently the roles only supports the deployment of SSL-enabled, Kerberos authenticated Kafka clusters (= `SASL_SSL` listeners + `GSSAPI` mechanism).

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- `kafka_2.13-3.2.0.tgz` available in `files` directory
- Group `kafka_broker` defined in the Ansible inventory
- Certificate of the CA available as `root.pem` in `files`
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` available in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided

## Example

The following hosts file and playbook are given as examples.

### Host file

```
[kafka_broker]
worker-01
worker-02
worker-03

[kafka_client]
edge-01
```

### Available Playbooks

- [kafka](../../playbooks/kafka.yml) deploys:
  - Kafka Broker
  - Kafka Client
