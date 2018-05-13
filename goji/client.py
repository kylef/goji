import os
import pickle
import json

import click
import requests
from requests.compat import urljoin

from goji.models import User, Issue, Transition, Sprint, Comment
from goji.auth import get_credentials


class JIRAException(click.ClickException):
    def __init__(self, error_messages, errors):
        self.error_messages = error_messages
        self.errors = errors

    def show(self):
        for error in self.error_messages:
            click.echo(error)

        for (key, error) in self.errors.items():
            click.echo('- {}: {}'.format(key, error))


class JIRAClient(object):
    def __init__(self, base_url, auth=None):
        self.session = requests.Session()
        self.base_url = base_url
        self.rest_base_url = urljoin(self.base_url, 'rest/api/2/')
        self.session.auth = auth
        self.load_cookies()

    # Persistent Cookie

    @property
    def cookie_path(self):
        return os.path.expanduser('~/.goji/cookies')

    def load_cookies(self):
        if os.path.exists(self.cookie_path):
            try:
                with open(self.cookie_path, 'rb') as fp:
                    self.session.cookies = pickle.load(fp)
            except Exception as e:
                print('warning: Could not load cookies from dist: ' + e)

    def save_cookies(self):
        cookies = self.session.cookies.keys()
        cookies.remove('atlassian.xsrf.token')

        if len(cookies) > 0:
            os.makedirs(os.path.expanduser('~/.goji'), exist_ok=True)

            with open(self.cookie_path, 'wb') as fp:
                pickle.dump(self.session.cookies, fp)
        elif os.path.exists(self.cookie_path):
            os.remove(self.cookie_path)

    # Methods

    def validate_response(self, response):
        if response.status_code >= 400 and 'application/json' in response.headers.get('Content-Type', ''):
            error = response.json()
            raise JIRAException(error.get('errorMessages', []), error.get('errors', {}))

    def get(self, path, **kwargs):
        url = urljoin(self.rest_base_url, path)
        response = self.session.get(url, **kwargs)
        self.validate_response(response)
        return response

    def post(self, path, json):
        url = urljoin(self.rest_base_url, path)
        response = self.session.post(url, json=json)
        self.validate_response(response)
        return response

    def put(self, path, json):
        url = urljoin(self.rest_base_url, path)
        response = self.session.put(url, json=json)
        self.validate_response(response)
        return response

    @property
    def username(self):
        return self.session.auth[0]

    def get_user(self):
        response = self.get('myself', allow_redirects=False)
        response.raise_for_status()
        return User.from_json(response.json())

    def get_issue(self, issue_key):
        response = self.get('issue/%s' % issue_key)
        response.raise_for_status()
        return Issue.from_json(response.json())

    def get_issue_transitions(self, issue_key):
        response = self.get('issue/%s/transitions' % issue_key)
        response.raise_for_status()
        return map(Transition.from_json, response.json()['transitions'])

    def change_status(self, issue_key, transition_id):
        data = {'transition': {'id': transition_id}}
        response = self.post('issue/%s/transitions' % issue_key, data)
        return (response.status_code == 204)

    def edit_issue(self, issue_key, updated_fields):
        data = {'fields': updated_fields}
        response = self.put('issue/%s' % issue_key, data)
        return (response.status_code == 204) or (response.status_code == 200)

    def create_issue(self, fields):
        response = self.post('issue', {'fields': fields})
        return Issue.from_json(response.json())

    def assign(self, issue_key, name):
        response = self.put('issue/%s/assignee' % issue_key, {'name': name})

    def comment(self, issue_key, comment):
        response = self.post('issue/%s/comment' % issue_key, {'body': comment})
        return Comment.from_json(response.json())

    def search(self, query):
        response = self.post('search', {'jql': query})
        response.raise_for_status()
        return list(map(Issue.from_json, response.json()['issues']))

    def create_sprint(self, board_id, name, start_date=None, end_date=None):
        payload = {
            'originBoardId': board_id,
            'name': name,
        }

        if start_date:
            payload['startDate'] = start_date.isoformat()

        if end_date:
            payload['endDate'] = end_date.isoformat()

        url = urljoin(self.base_url, 'rest/agile/1.0/sprint')
        response = self.session.post(url, json=payload)
        self.validate_response(response)
        return Sprint.from_json(response.json())
