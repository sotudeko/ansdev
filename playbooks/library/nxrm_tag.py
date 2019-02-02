#!/usr/bin/python

DOCUMENTATION = '''
---
module: nxrm_tag
short_description: Manage your tags in Nexus Repository 3
description:
  - Interacts with the specified Nexus Repository 3 instance to create and delete tags
options:
  repo_url:
    description:
      - HTTP or HTTPS URL in the form of (http|https)://host:domain[:port]
    required: true
    default: http://localhost:8081
  tag_name:
    description:
      - name of the tag (This is mutually exclusive with the body option)
    required: false
    default: null
  user:
    description:
      - user name to use to log in to Nexus Repository
    required: true
    default: admin
  password:
    description:
      - user password to log in to Nexus Repository
    required: true
    default: admin123
  state:
    description:
      - If C(present), the tag will be created, If C(absent), the tag will be removed
    required: true
    default: true
    choices: [ present, absent ]
  body:
    description:
      - The body of the http request/response to the Nexus Repository. It must be an already formatted JSON string.
    required: false
    default: null

'''

EXAMPLES = '''
- name: Create a tag
  nxrm_tag:
    repo_url: "http://localhost:8081"
    tag_name: "my-tag-name"
    user: admin
    password: admin123
    state: present
    body: "{{lookup('file', 'tagfile.json')}}"
  register: result

- name: Delete a tag
  nxrm_tag:
    repo_url: "http://localhost:8081"
    tag_name: "my-tag-name"
    user: admin
    password: admin123
    state: absent
  register: result
'''

from ansible.module_utils.basic import *
import requests
import json

from requests.auth import HTTPBasicAuth

tags_api = '/service/rest/v1/tags'

def create_tag(data):
    has_changed = False

    repo_url = data['repo_url']
    user = data['user']
    password = data['password']
    body = data['body']
    tag_name = data['tag_name']

    if tag_name is not None and body is not None:
        meta = {'status': -1, 'response': 'Cannot specify both tag_name and body'}
        return (has_changed, meta)

    url = "{}{}" . format(repo_url, tags_api)
    headers = {"Content-Type": "application/json", "accept": "application/json"}

    result = requests.post(url, json.dumps(body), auth=(user, password), headers=headers)
    meta = {"status": result.status_code, 'response': result.content}

    if result.status_code == 200:
        has_changed = True

    return (has_changed, meta)

def delete_tag(data):
    has_changed = False

    repo_url = data['repo_url']
    user = data['user']
    password = data['password']
    body = data['body']
    tag_name = data['tag_name']

    if body is not None:
        meta = {'status': -1, 'response': 'Cannot use body to delete a tag. Use tag_name instead'}
        return (has_changed, meta)

    if tag_name is None:
        meta = {'status': -1, 'response': 'no tag_name specified'}
        return (has_changed, meta)

    url = "{}{}{}{}" . format(repo_url, tags_api, '/', tag_name)
    headers = {"Content-Type": "application/json", "accept": "application/json"}
    result = requests.delete(url, auth=(user, password), headers=headers)

    meta = {"status": result.status_code, 'response': result.content}

    if result.status_code == 200:
        has_changed = True

    if result.status_code == 204:
        has_changed = True

    return (has_changed, meta)

def main():

    fields = {
		"user": {"default": "admin", "required": False, "type": "str"},
        "password": {"default": "admin123", "required": False, "type": "str", "no_log": True},
        "repo_url": {"default": "http://localhost:8081", "required": False, "type": "str" },
		"tag_name": {"required": False, "type": "str" },
        "body": {"required": False, "type": "raw"},
        "state": {
        	"default": "present", 
        	"choices": ['present', 'absent'],  
        	"type": 'str' 
        } 
	}

    choice_map = {
      "present": create_tag,
      "absent": delete_tag, 
    }
    
    module = AnsibleModule(argument_spec=fields)
    has_changed, result = choice_map.get(module.params['state'])(module.params)
    module.exit_json(changed=has_changed, meta=result)

if __name__ == '__main__':
    main()

 
