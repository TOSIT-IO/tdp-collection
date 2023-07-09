#!/usr/bin/python
# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common._collections_compat import Mapping, Sequence
from ansible.module_utils.six import iteritems, string_types, text_type
from ansible.module_utils.six.moves.urllib.parse import quote as urlquote
from ansible.module_utils.urls import fetch_url, url_argument_spec

def ranger_json_deep_equal(a, b):
    """Custom comparison of two objects.
    If objects are Mapping (dict) and if B has a missing key from A return False. If B has additional keys returns True.
    Ranger Admin can return JSON with additional keys and we should ignore it.
    """
    if isinstance(a, Mapping) and isinstance(b, Mapping):
        for key_a, value_a in iteritems(a):
            if key_a not in b:
                return False
            if not ranger_json_deep_equal(value_a, b[key_a]):
                return False
    # "string_types" is a "Sequence", to avoid infinite recursion perform direct comparison
    elif isinstance(a, string_types) and isinstance(b, string_types):
        # Convert to unicode before comparison
        return text_type(a) == text_type(b)
    elif isinstance(a, Sequence) and isinstance(b, Sequence):
        if len(a) != len(b):
            return False
        for value_a, value_b in zip(a, b):
            if not ranger_json_deep_equal(value_a, value_b):
                return False
    return a == b

def dict_del_key(a, b):
    """Remove keys in B that are not in A recursively"""
    if isinstance(a, Mapping) and isinstance(b, Mapping):
        for key_b in list(b.keys()):
            if key_b not in a:
                del b[key_b]
            else:
                dict_del_key(a[key_b], b[key_b])
    # "string_types" is a "Sequence", to avoid infinite recursion return
    elif isinstance(a, string_types) and isinstance(b, string_types):
        return
    elif isinstance(a, Sequence) and isinstance(b, Sequence):
        for value_a, value_b in zip(a, b):
            dict_del_key(value_a, value_b)

def main():
    argument_spec = url_argument_spec()
    argument_spec.update(
        policy_mgr_url=dict(type='str', required=True),
        policy=dict(type='dict', required=True),
        state=dict(type='str', choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    policy_mgr_url = module.params['policy_mgr_url']
    policy = module.params['policy']
    state = module.params['state'] or 'present'

    # Ranger Admin does not expect "state" key
    if "state" in policy:
        del policy['state']

    try:
        name = policy['name']
    except KeyError:
        module.fail_json(msg='"name" is required in policy dict')
    try:
        service = policy['service']
    except KeyError:
        module.fail_json(msg='"service" is required in policy dict')

    name_urlquote = urlquote(name)
    service_urlquote = urlquote(service)
    ranger_url_get_policy = '{}/service/public/v2/api/service/{}/policy/{}'.format(policy_mgr_url, service_urlquote, name_urlquote)
    ranger_url_put_policy = ranger_url_get_policy
    ranger_url_post_policy = '{}/service/public/v2/api/policy'.format(policy_mgr_url)
    ranger_url_delete_policy = '{}/service/public/v2/api/policy?servicename={}&policyname={}'.format(policy_mgr_url, service_urlquote, name_urlquote)
    headers = {
        'Accept': 'application/json',
    }
    post_put_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    try:
        results = {
            'changed': False,
        }

        get_resp, get_info = fetch_url(module, ranger_url_get_policy, headers=headers, method='GET')
        get_status_code = get_info["status"]
        if get_status_code != 200 and get_status_code != 404:
            module.fail_json(msg='Error when getting Ranger policy "{}" in service "{}" with URL "{}", status code "{}"'.format(name, service, ranger_url_get_policy, get_status_code))

        # Case when policy is absent
        if get_status_code == 404:
            # Case when policy is absent and must be removed -> nothing to do
            if state == 'absent':
                return module.exit_json(**results)

            # Case when policy is absent and must be created
            results['changed'] = True
            if not module.check_mode:
                post_resp, post_info = fetch_url(module, ranger_url_post_policy, headers=post_put_headers, method='POST', data=json.dumps(policy))
                post_status_code = post_info['status']
                if post_status_code != 200:
                    module.fail_json(msg='Error when creating Ranger policy "{}" in service "{}" with URL "{}", status code "{}"'.format(name, service, ranger_url_post_policy, post_status_code))

        # Case when policy exists
        else:
            current_policy = json.load(get_resp)
            dict_del_key(policy, current_policy)

            # Case when policy exists and must be removed
            if state == 'absent':
                results['changed'] = True
                if not module.check_mode:
                    delete_resp, delete_info = fetch_url(module, ranger_url_delete_policy, headers=headers, method='DELETE')
                    delete_status_code = delete_info['status']
                    if delete_status_code != 204:
                        module.fail_json(msg='Error when deleting Ranger policy "{}" in service "{}" with URL "{}", status code "{}"'.format(name, service, ranger_url_delete_policy, delete_status_code))

            # Case when policy exists and must be present -> compare with current policy if an update is needed
            elif not ranger_json_deep_equal(policy, current_policy):
                results['changed'] = True
                if module._diff:
                    diff = results.setdefault('diff', {})
                    diff['before'] = json.dumps(current_policy, sort_keys=True, indent=4) + '\n'
                    diff['after'] = json.dumps(policy, sort_keys=True, indent=4) + '\n'
                if not module.check_mode:
                    put_resp, put_info = fetch_url(module, ranger_url_put_policy, headers=post_put_headers, method='PUT', data=json.dumps(policy))
                    put_status_code = put_info['status']
                    if put_status_code != 200:
                        module.fail_json(msg='Error when updating Ranger policy "{}" in service "{}" with URL "{}", status code "{}"'.format(name, service, ranger_url_put_policy, put_status_code))

        module.exit_json(**results)

    except Exception:
        import traceback
        module.fail_json(msg=to_native(traceback.format_exc()))

if __name__ == '__main__':
    main()
