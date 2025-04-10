#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests
import json

def get_target_group(module, api_url, auth, group_id):
    url = f"{api_url}/api/targetgroups/{group_id}"
    r = requests.get(url, auth=auth, verify=False)
    if r.status_code == 404:
        return None
    elif r.status_code != 200:
        module.fail_json(msg=f"Failed to get target group: {r.status_code} {r.text}")
    return r.json()

def create_target_group(module, api_url, auth, payload):
    url = f"{api_url}/api/targetgroups"
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, auth=auth, headers=headers, data=json.dumps(payload), verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to create target group: {r.status_code} {r.text}")

def delete_target_group(module, api_url, auth, group_id):
    url = f"{api_url}/api/targetgroups/{group_id}"
    r = requests.delete(url, auth=auth, verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to delete target group: {r.status_code} {r.text}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            group_name=dict(type='str', required=True),
            description=dict(type='str', required=False),
            session=dict(type='dict', required=False),
            password_retrieval=dict(type='dict', required=False, no_log=False),
            restrictions=dict(type='list', elements='dict', required=False),
            api_url=dict(type='str', required=True),
            wallix_user=dict(type='str', required=True),
            wallix_password=dict(type='str', required=True, no_log=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True
    )

    p = module.params
    auth = (p['wallix_user'], p['wallix_password'])
    group_id = p['group_name']

    existing = get_target_group(module, p['api_url'], auth, group_id)

    if p['state'] == 'present':
        if existing:
            module.exit_json(changed=False, msg="Target group already exists.")
        if module.check_mode:
            module.exit_json(changed=True)

        payload = {
            "group_name": p['group_name'],
            "description": p['description'],
            "session": p['session'],
            "password_retrieval": p['password_retrieval'],
            "restrictions": p['restrictions']
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        create_target_group(module, p['api_url'], auth, payload)
        module.exit_json(changed=True, msg="Target group created.")

    elif p['state'] == 'absent':
        if not existing:
            module.exit_json(changed=False, msg="Target group already absent.")
        if module.check_mode:
            module.exit_json(changed=True)
        delete_target_group(module, p['api_url'], auth, group_id)
        module.exit_json(changed=True, msg="Target group deleted.")

if __name__ == '__main__':
    main()
