#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests
import json

def get_authorization(module, api_url, auth, authorization_id):
    url = f"{api_url}/api/authorizations/{authorization_id}"
    r = requests.get(url, auth=auth, verify=False)
    if r.status_code == 404:
        return None
    elif r.status_code != 200:
        module.fail_json(msg=f"Failed to get authorization: {r.status_code} {r.text}")
    return r.json()

def create_authorization(module, api_url, auth, payload):
    url = f"{api_url}/api/authorizations"
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, auth=auth, headers=headers, data=json.dumps(payload), verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to create authorization: {r.status_code} {r.text}")

def update_authorization(module, api_url, auth, authorization_id, payload):
    url = f"{api_url}/api/authorizations/{authorization_id}?force=true"
    headers = {'Content-Type': 'application/json'}
    r = requests.put(url, auth=auth, headers=headers, data=json.dumps(payload), verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to update authorization: {r.status_code} {r.text}")

def delete_authorization(module, api_url, auth, authorization_id):
    url = f"{api_url}/api/authorizations/{authorization_id}"
    r = requests.delete(url, auth=auth, verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to delete authorization: {r.status_code} {r.text}")

def is_authorization_different(existing, desired):
    def normalize(val):
        if isinstance(val, list):
            return sorted(val)
        return val

    for key, value in desired.items():
        if key not in existing:
            return True
        if normalize(existing[key]) != normalize(value):
            return True

    for key in existing:
        if key in ["subprotocols"] and key not in desired:
            return True
        if isinstance(existing.get(key), list) and desired.get(key) is None:
            return True

    return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            authorization_name=dict(type='str', required=True),
            user_group=dict(type='str', required=True),
            target_group=dict(type='str', required=True),
            description=dict(type='str', required=False),
            subprotocols=dict(type='list', elements='str', required=False),
            is_critical=dict(type='bool', required=False, default=False),
            is_recorded=dict(type='bool', required=False, default=False),
            authorize_password_retrieval=dict(type='bool', required=False, default=False, no_log=False),
            authorize_sessions=dict(type='bool', required=False, default=False),
            approval_required=dict(type='bool', required=False, default=False),
            has_comment=dict(type='bool', required=False),
            mandatory_comment=dict(type='bool', required=False),
            has_ticket=dict(type='bool', required=False),
            mandatory_ticket=dict(type='bool', required=False),
            approvers=dict(type='list', elements='str', required=False),
            active_quorum=dict(type='int', required=False),
            inactive_quorum=dict(type='int', required=False),
            single_connection=dict(type='bool', required=False),
            approval_timeout=dict(type='int', required=False),
            authorize_session_sharing=dict(type='bool', required=False, default=False),
            session_sharing_mode=dict(type='str', required=False),
            api_url=dict(type='str', required=True),
            wallix_user=dict(type='str', required=True),
            wallix_password=dict(type='str', required=True, no_log=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True
    )

    p = module.params
    auth = (p['wallix_user'], p['wallix_password'])
    authorization_id = p['authorization_name']

    existing = get_authorization(module, p['api_url'], auth, authorization_id)

    mutable_fields = [
        "description", "subprotocols", "is_critical", "is_recorded",
        "authorize_password_retrieval", "authorize_sessions",
        "authorize_session_sharing", "session_sharing_mode",
        "approval_required"
    ]

    approval_only_fields = [
        "approvers", "has_comment", "mandatory_comment",
        "has_ticket", "mandatory_ticket",
        "active_quorum", "inactive_quorum",
        "single_connection", "approval_timeout"
    ]

    create_payload = {
        "authorization_name": p['authorization_name'],
        "user_group": p['user_group'],
        "target_group": p['target_group']
    }

    update_payload = {}

    for field in mutable_fields:
        if p.get(field) is not None:
            create_payload[field] = p[field]
            update_payload[field] = p[field]

    if p["approval_required"]:
        for field in approval_only_fields:
            if p.get(field) is not None:
                create_payload[field] = p[field]
                update_payload[field] = p[field]

    if p['state'] == 'present':
        if not existing:
            if module.check_mode:
                module.exit_json(changed=True)
            create_authorization(module, p['api_url'], auth, create_payload)
            module.exit_json(changed=True, msg="Authorization created.")
        else:
            if is_authorization_different(existing, update_payload):
                if module.check_mode:
                    module.exit_json(changed=True)
                update_authorization(module, p['api_url'], auth, authorization_id, update_payload)
                module.exit_json(changed=True, msg="Authorization updated.")
            else:
                module.exit_json(changed=False, msg="Authorization already up to date.")

    elif p['state'] == 'absent':
        if not existing:
            module.exit_json(changed=False, msg="Authorization already absent.")
        if module.check_mode:
            module.exit_json(changed=True)
        delete_authorization(module, p['api_url'], auth, authorization_id)
        module.exit_json(changed=True, msg="Authorization deleted.")

if __name__ == '__main__':
    main()
