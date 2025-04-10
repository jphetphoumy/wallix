#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests
import json

def get_group(module, api_url, auth, group_id):
    url = f"{api_url}/api/usergroups/{group_id}"
    r = requests.get(url, auth=auth, verify=False)

    if r.status_code == 404:
        return None
    elif r.status_code != 200:
        module.fail_json(msg=f"Failed to get group: {r.status_code} {r.text}")
    return r.json()

def create_group(module, api_url, auth, payload):
    url = f"{api_url}/api/usergroups"
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, auth=auth, headers=headers, data=json.dumps(payload), verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to create group: {r.status_code} {r.text}")

def delete_group(module, api_url, auth, group_id):
    url = f"{api_url}/api/usergroups/{group_id}"
    r = requests.delete(url, auth=auth, verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to delete group: {r.status_code} {r.text}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            group_name=dict(type='str', required=True),
            description=dict(type='str', required=False),
            timeframes=dict(type='list', elements='str', required=False),
            users=dict(type='list', elements='str', required=False),
            profile=dict(type='str', required=False),
            language=dict(type='str', required=False),
            email_list=dict(type='str', required=False),
            restrictions=dict(type='list', elements='dict', required=False),
            api_url=dict(type='str', required=True),
            wallix_user=dict(type='str', required=True),
            wallix_password=dict(type='str', required=True, no_log=True),
            state=dict(type='str', choices=['present', 'absent'], default='present')
        ),
        supports_check_mode=True
    )

    params = module.params
    auth = (params['wallix_user'], params['wallix_password'])
    group_id = params['group_name']
    state = params['state']

    group = get_group(module, params['api_url'], auth, group_id)

    if state == 'present':
        if group:
            module.exit_json(changed=False, msg="Group already exists.")
        if module.check_mode:
            module.exit_json(changed=True)
        payload = {
            "group_name": group_id,
            "description": params['description'],
            "timeframes": params['timeframes'],
            "users": params['users'],
            "profile": params['profile'],
            "language": params['language'],
            "email_list": params['email_list'],
            "restrictions": params['restrictions']
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        create_group(module, params['api_url'], auth, payload)
        module.exit_json(changed=True, msg="Group created.")

    elif state == 'absent':
        if not group:
            module.exit_json(changed=False, msg="Group already absent.")
        if module.check_mode:
            module.exit_json(changed=True)
        delete_group(module, params['api_url'], auth, group_id)
        module.exit_json(changed=True, msg="Group deleted.")

if __name__ == '__main__':
    main()
