# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.errors import AnsibleOptionsError
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils.six import string_types
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible.utils.vars import merge_hash
from ansible_collections.tosit.tdp.plugins.module_utils.constants import (
    PREFIX, SEPARATOR_CHAR
)

MANDATORY_GROUPS = [PREFIX + "all", PREFIX + "tdp-cluster", PREFIX + "hadoop"]

display = Display()

# Example:
#   node_name: hdfs_datanode_conf
#   result: ["hdfs", "hdfs_datanode", "hdfs_datanode_conf"]
def get_node_groups_from_node_name(node_name):
    splits = node_name.split(SEPARATOR_CHAR)
    node_groups = [PREFIX + splits[0]]
    for i, split_value in enumerate(splits[1:], start=1):
        node_groups.append(node_groups[i - 1] + SEPARATOR_CHAR + split_value)
    return node_groups


def get_vars(task_vars, node_name):
    # Get node name vars if it exists
    groups = MANDATORY_GROUPS + get_node_groups_from_node_name(node_name)
    for group in reversed(groups):
        # loop through all groups in reverse returns the first present in vars
        # loaded and merged by inventory plugin
        vars = task_vars.get(group)
        if vars:
            display.v("vars loaded: " + group)
            return vars

    # no groups were found
    return {}


class ActionModule(ActionBase):
    _VALID_ARGS = frozenset(["node_name"])

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = {}
        result = super(ActionModule, self).run(tmp, task_vars)
        node_name = self._task.args.get("node_name", None)
        if node_name is None or not isinstance(node_name, string_types):
            raise AnsibleOptionsError(
                "'node_name' must be set to a valid string node name"
            )

        display.v("Node Name: " + node_name)
        # Current node vars
        vars = get_vars(task_vars, node_name)
        # merge node vars with task vars, with task vars (hostvars/group vars) having
        # precedence over tdp_vars
        vars_merged_with_task_vars = merge_hash(vars, task_vars)

        # Make merged variables available to template engine
        self._templar.available_variables = vars_merged_with_task_vars
        # Template the merged dict using ansible templating engine
        result["ansible_facts"] = self._template_with_keys(vars)
        result["changed"] = False
        return result

    def _template_with_keys(self, value_to_template):
        if isinstance(value_to_template, Mapping):
            return {
                self._templar.template(key): self._template_with_keys(value)
                for key, value in value_to_template.items()
            }
        return self._templar.template(value_to_template)
