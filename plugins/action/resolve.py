# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.module_utils.six import string_types
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible.utils.vars import merge_hash

from ansible_collections.tosit.tdp.plugins.module_utils.constants import PREFIX

display = Display()

ORDER = {
    "all": 0,
    "hadoop": 1,
    "super_group": 2,
    "current": 999,
}


def get_node_groups_from_node_name(node_name):
    splits = node_name.split("_")
    node_groups = [splits[0]]
    for i, split_value in enumerate(splits[1:], start=1):
        node_groups.append(node_groups[i - 1] + "_" + split_value)
    return node_groups


def merge_order(groups, node_groups, target):
    # all and hadoop are always kept if they exists
    forced_kept_keys = frozenset(["all", "hadoop"])
    order = {}
    for key in forced_kept_keys:
        if key in groups:
            order[key] = ORDER[key]
            groups.remove(key)
    # sort should be lexicographically correct as long there are no caps involved
    # if we want to assure lexicographic order, we can add parameter key=str.lower
    # which will apply the lower() function to every strings
    groups.sort()
    for i, group in enumerate(groups):
        if group in node_groups and group != target:
            order[group] = ORDER["super_group"] + i
        elif group == target:
            order[group] = ORDER["current"]

    return order


class ActionModule(ActionBase):
    _VALID_ARGS = frozenset(["node_name"])

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = {}
        result = super(ActionModule, self).run(tmp, task_vars)
        node_name = self._task.args.get("node_name", None)
        if node_name is None or not isinstance(node_name, string_types):
            raise AnsibleError("'node_name' must be set to a valid string node name")

        node_groups = get_node_groups_from_node_name(node_name)

        display.v("Node Name: " + node_name)
        display.v("Prefix: " + PREFIX)
        display.v("Node groups: " + ",".join(node_groups))

        tdp_keys = list(
            key[len(PREFIX) :] for key in task_vars.keys() if key.startswith(PREFIX)
        )
        display.v("Tdp Keys: " + ",".join(tdp_keys))

        order = merge_order(tdp_keys, node_groups, node_name)
        display.v("Merge order: " + str(order))
        groups = sorted(order.keys(), key=lambda group: order[group])
        display.v("Group order: " + str(groups))
        if len(groups) > 0:
            vars = task_vars.get(PREFIX + groups[0], {})
            for group in groups[1:]:
                vars = merge_hash(vars, task_vars.get(PREFIX + group, {}))
            # HostVars are more important than a group var
            vars_merged_with_task_vars = merge_hash(vars, task_vars)
            self._templar.available_variables = vars_merged_with_task_vars
            result["ansible_facts"] = {
                key: self._templar.template(vars_merged_with_task_vars[key])
                for key in vars
            }
        result["changed"] = False
        return result
