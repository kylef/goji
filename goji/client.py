import json

import requests
from requests.compat import urljoin

from goji.models import User, Issue, Transition
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

    def get(self, path):
        url = urljoin(self.rest_base_url, path)
        return requests.get(url, auth=self.auth)

    def post(self, path, json):
        url = urljoin(self.rest_base_url, path)
        return requests.post(url, auth=self.auth, json=json)

    def put(self, path, json):
        url = urljoin(self.rest_base_url, path)
        return requests.put(url, auth=self.auth, json=json)

    @property
    def username(self):
        return self.auth[0]

    def get_user(self):
        response = self.get('myself')
        return User.from_json(response.json())

    def get_issue(self, issue_key):
        response = self.get('issue/%s' % issue_key)
        return Issue.from_json(response.json())

    def get_issue_transitions(self, issue_key):
        response = self.get('issue/%s/transitions' % issue_key)
        return map(Transition.from_json, response.json()['transitions'])

    def change_status(self, issue_key, transition_id):
        data = {'transition': {'id': transition_id}}
        response = self.post('issue/%s/transitions' % issue_key, data)
        return (response.status_code == 204)

    def edit_issue(self, issue_key, updated_fields):
        data = {'fields': updated_fields}
        response = self.put('issue/%s' % issue_key, data)
        return (response.status_code == 204) or (response.status_code == 200)

    def assign(self, issue_key, name):
        response = self.put('issue/%s/assignee' % issue_key, {'name': name})
        return (response.status_code == 204) or (response.status_code == 200)

    def comment(self, issue_key, comment):
        response = self.post('issue/%s/comment' % issue_key, {'body': comment})
        return (response.status_code == 201) or (response.status_code == 200)

    def search(self, query):
        response = self.post('search', {'jql': query})
        return map(Issue.from_json, response.json()['issues'])
