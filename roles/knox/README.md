# Ansible Knox TDP

This is the main Knox directory. It includes the following sub-role:

- Knox Gateway Application

## Prerequisites

- `java-1.8.0-openjdk` and `krb5-workstation` installed on all nodes
- Knox TDP release .tar.gz (`knox_dist_file` role variable) file available in `files`
- Knoxshell TDP release .tar.gz (`knoxshell_dist_file` role variable) file available in `files`
- Ranger TDP Knox plugin release .tar.gz (`ranger_knox_dist_file` role variable) file available in `files`
- Group `knox` defined in the Ansible inventory
- Certificate of the CA available as `root.pem` in `files`
- Certificate files `{{ fqdn }}.key` and `{{ fqdn }}.pem` available in `files`
- Admin access to a KDC with the `realm`, `kadmin_principal` and `kadmin_password` role vars provided

## Example

The following hosts file and playbook are given as examples.

### Host file

```ini
[knox]
tdp-edge-1
```

### Available Playbooks

- [knox.yml](../../playbooks/knox.yml) deploys:
  - Knox Gateway

- [ranger_plugins_knox.yml](../../playbooks/ranger_plugins_knox.yml) deploys:
  - Ranger Knox plugin

## Additional notes

- Keystore creation uses `-srcalias` and `-destalias gateway-identity`
- Generate Knox master secret using interactive tool `expect`

## TODO

Please check out the [Knox related issues](https://github.com/TOSIT-IO/ansible-tdp-roles/issues?q=is%3Aopen+is%3Aissue+label%3Aknox).
