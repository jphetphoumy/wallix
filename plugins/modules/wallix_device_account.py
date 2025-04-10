from ansible.module_utils.basic import AnsibleModule
import requests
import json

def get_account(module, api_url, auth, device_id, domain_id, account_id):
    url = f"{api_url}/api/devices/{device_id}/localdomains/{domain_id}/accounts/{account_id}"
    r = requests.get(url, auth=auth, verify=False)
    if r.status_code == 404:
        return None
    elif r.status_code != 200:
        module.fail_json(msg=f"Failed to get account: {r.status_code} {r.text}")
    return r.json()

def create_account(module, api_url, auth, device_id, domain_id, payload):
    url = f"{api_url}/api/devices/{device_id}/localdomains/{domain_id}/accounts"
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, auth=auth, headers=headers, data=json.dumps(payload), verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to create account {r.json()['description']}")

def delete_account(module, api_url, auth, device_id, domain_id, account_id):
    url = f"{api_url}/api/devices/{device_id}/localdomains/{domain_id}/accounts/{account_id}"
    r = requests.delete(url, auth=auth, verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to delete account: {r.status_code} {r.text}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            account_name=dict(type='str', required=True),
            account_login=dict(type='str', required=False),
            description=dict(type='str', required=False),
            credentials=dict(type='list', elements='dict', required=False),
            checkout_policy=dict(type='str', required=False, default='default'),
            device_id=dict(type='str', required=True),
            domain_id=dict(type='str', required=True),
            api_url=dict(type='str', required=True),
            wallix_user=dict(type='str', required=True),
            wallix_password=dict(type='str', required=True, no_log=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True
    )

    p = module.params
    auth = (p['wallix_user'], p['wallix_password'])
    account = get_account(module, p['api_url'], auth, p['device_id'], p['domain_id'], p['account_name'])

    if p['state'] == 'present':
        if account:
            module.exit_json(changed=False, msg="Account already exists.")

        if module.check_mode:
            module.exit_json(changed=True)

        payload = {
            "account_name": p['account_name'],
            "account_login": p.get('account_login', p['account_name']),
            "description": p['description'],
            "credentials": p['credentials'],
            "checkout_policy": p['checkout_policy'],
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        create_account(module, p['api_url'], auth, p['device_id'], p['domain_id'], payload)
        module.exit_json(changed=True, msg="Account created.")

    elif p['state'] == 'absent':
        if not account:
            module.exit_json(changed=False, msg="Account already absent.")
        if module.check_mode:
            module.exit_json(changed=True)
        delete_account(module, p['api_url'], auth, p['device_id'], p['domain_id'], p['account_name'])
        module.exit_json(changed=True, msg="Account deleted.")

if __name__ == '__main__':
    main()

