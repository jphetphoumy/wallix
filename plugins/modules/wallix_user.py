#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests
import json

DOCUMENTATION = r'''
---
module: wallix_user

short_description: Manage Wallix users via REST API

description: Create, update or delete users in Wallix Bastion.

options:
  name:
    description: The user name.
    required: true
    type: str
  state:
    description: Whether the user should be present or absent.
    default: present
    choices: [present, absent]
    type: str
  profile:
    description: The profile to use for the user
    required: true
    type: str
  user_auths:
    description: The authentication of the user
    required: true
    type: str 
  email:
    description: User email address.
    required: false
    type: str
  display_name:
    description: Full name of the user.
    required: false
    type: str
  password:
    description: User password (required if no SSH key or cert).
    required: false
    type: str
  ssh_public_key:
    description: Ssh public key (required if local_sshkey)
    required: false
    type: str
  groups:
    description: List of groups the user belongs to.
    type: list
    elements: str
  ip_source:
    description: IP source of the user.
    type: str
  preferred_language:
    description: Language preference.
    type: str
  expiration_date:
    description: User expiration date.
    type: str
  force_change_pwd:
    description: Force password change on next login.
    type: bool
    default: false
  user_auths:
    description: Authentication methods.
    type: list
    elements: str
  api_url:
    description: Base URL of the Wallix API.
    required: true
    type: str

author:
  - You 😉
'''

EXAMPLES = r'''
- name: Create a Wallix user
  wallix_user:
    name: jdoe
    display_name: John Doe
    email: john.doe@example.com
    password: my_secret_password
    groups:
      - user_group1
    ip_source: 10.10.47.10
    preferred_language: fr
    force_change_pwd: true
    user_auths:
      - local_password
    expiration_date: "2016-12-31 23:59"
    api_url: "https://example.com"
    state: present
'''

RETURN = r'''
changed:
  description: Whether anything was changed.
  type: bool
  returned: always
'''

def get_user(module, api_url, wallix_user, wallix_password, username):
    url = f"{api_url}/api/users/{username}"
    #headers = {'Authorization': f'Bearer {token}'}
    auth = (wallix_user, wallix_password)
    r = requests.get(url, auth=auth, verify=False)

    if r.status_code == 404:
        return None
    elif r.status_code != 200:
        module.fail_json(msg=f"Failed to get user: {r.status_code} {r.text}")
    return r.json()

def create_user(module, api_url, wallix_user, wallix_password, payload):
    url = f"{api_url}/api/users"
    headers = {
        'Content-Type': 'application/json'
    }
    auth = (wallix_user, wallix_password)
    r = requests.post(url, auth=auth, headers=headers, data=json.dumps(payload), verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to create user: {r.status_code} {r.text}")

def delete_user(module, api_url, wallix_user, wallix_password, username):
    url = f"{api_url}/api/users/{username}"
    #headers = {'Authorization': f'Bearer {token}'}
    auth = (wallix_user, wallix_password)
    r = requests.delete(url, auth=auth, verify=False)
    if r.status_code != 204:
        module.fail_json(msg=f"Failed to delete user: {r.status_code} {r.text}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            display_name=dict(type='str', required=False),
            email=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True),
            ssh_public_key=dict(type='str', required=False),
            profile=dict(type='str', required=True),
            groups=dict(type='list', elements='str', required=False),
            ip_source=dict(type='str', required=False),
            preferred_language=dict(type='str', required=False),
            force_change_pwd=dict(type='bool', default=False),
            user_auths=dict(type='list', elements='str', required=False),
            expiration_date=dict(type='str', required=False),
            api_url=dict(type='str', required=True),
            wallix_user=dict(type='str', required=True),
            wallix_password=dict(type='str', required=True, no_log=True)
        ),
        supports_check_mode=True
    )

    params = module.params
    username = params['name']
    state = params['state']
    profile = params['profile']
    api_url = params['api_url']
    wallix_user = params['wallix_user']
    wallix_password = params['wallix_password']

    user = get_user(module, api_url, wallix_user, wallix_password, username)

    if state == 'present':
        if user:
            # Future: Implement diff logic
            module.exit_json(changed=False, msg="User already exists.")
        else:
            if module.check_mode:
                module.exit_json(changed=True)
            payload = {
                "user_name": username,
                "display_name": params['display_name'],
                "email": params['email'],
                "profile": params['profile'],
                "password": params['password'],
                "ssh_public_key": params['ssh_public_key'],
                "groups": params['groups'],
                "ip_source": params['ip_source'],
                "preferred_language": params['preferred_language'],
                "force_change_pwd": params['force_change_pwd'],
                "user_auths": params['user_auths'],
                "expiration_date": params['expiration_date']
            }
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            create_user(module, api_url, wallix_user, wallix_password, payload)
            module.exit_json(changed=True, msg="User created.")

    elif state == 'absent':
        if not user:
            module.exit_json(changed=False, msg="User already absent.")
        if module.check_mode:
            module.exit_json(changed=True)
        delete_user(module, api_url, wallix_user, wallix_password, username)
        module.exit_json(changed=True, msg="User deleted.")

if __name__ == '__main__':
    main()
