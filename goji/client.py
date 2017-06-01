import json

import requests
from requests.compat import urljoin

from goji.models import Issue, Transition
from goji.auth import get_credentials


class JIRAClient(object):
    def __init__(self, base_url):
        email, password = get_credentials(base_url)

        if email is not None and password is not None:
            self.auth = (email, password)
            self.base_url = base_url
            self.rest_base_url = urljoin(self.base_url, '/rest/api/2/')
        else:
            print('== Authentication not configured. Run `goji login`')
            exit()

    @property
    def username(self):
        return self.auth[0]

    def get_issue(self, issue_key):
        url = urljoin(self.rest_base_url, 'issue/%s' % issue_key)
        request = requests.get(url, auth=self.auth)
        return Issue.from_json(request.json())

    def get_issue_transitions(self, issue_key):
        url = urljoin(self.rest_base_url, 'issue/%s/transitions' % issue_key)
        request = requests.get(url, auth=self.auth)
        return map(Transition.from_json, request.json()['transitions'])

    def change_status(self, issue_key, transition_id):
        url = urljoin(self.rest_base_url, 'issue/%s/transitions' % issue_key)
        headers = {'content-type': 'application/json'}
        data = json.dumps({'transition': {'id': transition_id}})
        request = requests.post(url, data=data, headers=headers, auth=self.auth)
        return (request.status_code == 204)

    def edit_issue(self, issue_key, updated_fields):
        url = urljoin(self.rest_base_url, 'issue/%s' % issue_key)
        headers = {'content-type': 'application/json'}
        data = json.dumps({'fields': updated_fields})
        request = requests.put(url, data=data, headers=headers, auth=self.auth)
        return (request.status_code == 204) or (request.status_code == 200)

    def assign(self, issue_key, name):
        url = urljoin(self.rest_base_url, 'issue/%s/assignee' % issue_key)
        headers = {'content-type': 'application/json'}
        data = json.dumps({'name': name})
        request = requests.put(url, data=data, headers=headers, auth=self.auth)
        return (request.status_code == 204) or (request.status_code == 200)

    def comment(self, issue_key, comment):
        url = urljoin(self.rest_base_url, 'issue/%s/comment' % issue_key)
        headers = {'content-type': 'application/json'}
        payload = json.dumps({'body': comment})
        request = requests.post(url, data=payload, headers=headers,
                                auth=self.auth)
        return (request.status_code == 201) or (request.status_code == 200)

    def search(self, query):
        url = urljoin(self.rest_base_url, 'search')
        headers = {'content-type': 'application/json'}
        payload = json.dumps({'jql': query})
        request = requests.post(url, data=payload, headers=headers,
                                auth=self.auth)
        return map(Issue.from_json, request.json()['issues'])
