#!/usr/bin/python

DOCUMENTATION = '''
---
module: nxrm_tag_list
short_description: List all tags in a Nexus Repository
description:
  - Interacts with the specified Nexus Repository 3 instance to list all tags
options:
  repo_url:
    description:
      - HTTP or HTTPS URL in the form of (http|https)://host:domain[:port]
    required: true
    default: http://localhost:8081
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
'''

EXAMPLES = '''
- name: list tags
  nxrm_tag_list:
    repo_url: "http://localhost:8081"
    user: admin
    password: admin123
  register: result
'''

from ansible.module_utils.basic import *
import requests

from requests.auth import HTTPBasicAuth

tags_api = '/service/rest/v1/tags'

def list_tags(data):
    has_changed = False

    repo_url = data['repo_url']
    user = data['user']
    password = data['password']
    url = "{}{}" . format(repo_url, tags_api)
    result = requests.get(url, auth=(user, password))
    return (has_changed, result.json())

def main():

    fields = {
        "user": {"default": "admin", "required": False, "type": "str"},
        "password": {"default": "admin123", "required": False, "type": "str", "no_log": True},
        "repo_url": {"default": "http://localhost:8081", "required": False, "type": "str" },
	}

    module = AnsibleModule(argument_spec=fields)
    has_changed, result = list_tags(module.params)
    module.exit_json(changed=has_changed, meta=result)

if __name__ == '__main__':
    main()

 
