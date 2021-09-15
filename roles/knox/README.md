# Knox

## Example playbook

```yml
---
- name: "Install Knox"
  hosts: knox
  tasks:
    - import_role:
        name: tosit.tdp.knox
```
