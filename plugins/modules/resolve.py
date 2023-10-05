# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

from __future__ import absolute_import, division, print_function


# pylint: disable=invalid-name
__metaclass__ = type
# pylint: enable=invalid-name

DOCUMENTATION = """
module: resolve
short_description: >-
  sets facts for current context
notes:
- This plugin always runs on the execution node
- This plugin will not run on a managed node
"""

EXAMPLES = r"""
---
- name: Hadoop client Config
  hosts: hadoop_client
  tasks:
    - tosit.tdp.resolve: 
        node_name: hadoop_client
    - name: Configure hadoop client
      ansible.builtin.import_role:
        name: tosit.tdp.hadoop.client
        tasks_from: config
    - ansible.builtin.meta: clear_facts 
"""

RETURN = r"""
# TO-DO: Enter return values here
"""
