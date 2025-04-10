from ansible.module_utils.basic import AnsibleModule
import requests
import json

def get_device(module, api_url, auth, device_id):
    url = f"{api_url}/api/devices/{device_id}"
    r = requests.get(url, auth=auth, verify=False)
    if r.status_code == 404:
        return None
    elif r.status_code != 200:
        module.fail_json(msg=f"Failed to get device: {r.status_code} {r.text}")
    return r.json()

def create_device(module, api_url, auth, payload):
    url = f"{api_url}/api/devices"
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, auth=auth, headers=headers, data=json.dumps(payload), verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to create device: {r.status_code} {r.text}")

def delete_device(module, api_url, auth, device_id):
    url = f"{api_url}/api/devices/{device_id}"
    r = requests.delete(url, auth=auth, verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to delete device: {r.status_code} {r.text}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            device_name=dict(type='str', required=True),
            alias=dict(type='str', required=False),
            description=dict(type='str', required=False),
            host=dict(type='str', required=True),
            local_domains=dict(type='list', elements='dict', required=False),
            services=dict(type='list', elements='dict', required=False),
            tags=dict(type='list', elements='dict', required=False),
            api_url=dict(type='str', required=True),
            wallix_user=dict(type='str', required=True),
            wallix_password=dict(type='str', required=True, no_log=True),
            state=dict(type='str', choices=['present', 'absent'], default='present')
        ),
        supports_check_mode=True
    )

    params = module.params
    device_id = params['device_name']
    auth = (params['wallix_user'], params['wallix_password'])

    device = get_device(module, params['api_url'], auth, device_id)

    if params['state'] == 'present':
        if device:
            module.exit_json(changed=False, msg="Device already exists.")
        if module.check_mode:
            module.exit_json(changed=True)

        payload = {
            "device_name": params['device_name'],
            "alias": params['alias'],
            "description": params['description'],
            "host": params['host'],
            "local_domains": params['local_domains'],
            "services": params['services'],
            "tags": params['tags']
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        create_device(module, params['api_url'], auth, payload)
        module.exit_json(changed=True, msg="Device created.")

    elif params['state'] == 'absent':
        if not device:
            module.exit_json(changed=False, msg="Device already absent.")
        if module.check_mode:
            module.exit_json(changed=True)
        delete_device(module, params['api_url'], auth, device_id)
        module.exit_json(changed=True, msg="Device deleted.")

if __name__ == '__main__':
    main()

