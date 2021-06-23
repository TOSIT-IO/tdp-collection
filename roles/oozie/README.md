# Ansible Oozie TDP

This role deploys the Ranger TDP release. It installs:

- Oozie Server

Currently the role only supports the deployment of SSL-enabled, Kerberos authenticated Oozie Server instances.

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Oozie TDP release .tar.gz (`oozie_dist_file` role variable) file available in `files`
- Group `oozie_server` defined in the Ansible hosts file
- Role `ansible-hadoop` run on `oozie_server` node as `hadoop_client`
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` for every node available in `files`
- Certificate of the CA available as `root.pem` in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided
- A `krb5.conf` file with this KDC informations must be available at `files/krb5.conf`

## Example

The following hosts file and playbook are given as examples.

### Host file

```
[ranger_admin]
tdp-ranger-1
```

### Playbook

```yaml
- name: "Deploy Oozie"
  hosts: oozie_server
  collections:
    - tosit.tdp
  roles:
    - role: oozie
      vars:
        realm: REALM.COM
        kadmin_principal: admin@REALM.COM
        kadmin_password: XXXXXXXX
        princ_password: p@ssw0rd123
        oozie_site:
          oozie.service.JPAService.jdbc.driver: com.mysql.jdbc.Driver
          oozie.service.JPAService.jdbc.url: jdbc:mysql://tdp-db-1.lxd:3306/oozie
          oozie.service.JPAService.jdbc.username: oozie
          oozie.service.JPAService.jdbc.password: oozie123
```

## Post-installation tasks

Currently, the following post-installation must be run manually before starting all services:

```
systemctl start oozie-server
```

## Useful commands

### Check the status of Oozie server

```
export OOZIE_CLIENT_OPTS='-Djavax.net.ssl.trustStore=/etc/ssl/certs/truststore.jks'
bin/oozie admin -status -oozie https://tdp-oozie-1.lxd:11443/oozie
```

## TODO

- [ ] Automate the activation of the webui with ExtJS
- [ ] Create a Oozie client submodule
- [ ] Make the choice between MySQL / Postgres configurable
- [ ] Make the DB / sharelib creation idempotent
