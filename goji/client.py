import datetime
import mimetypes
import os
import pickle
from typing import Any, Generator, List, Optional

import click
import requests
from requests.auth import AuthBase, HTTPBasicAuth
from requests.compat import urljoin

from goji.models import (
    Attachment,
    Comment,
    Comments,
    Issue,
    SearchResults,
    Sprint,
    Transition,
    UserDetails,
)


class JIRAException(click.ClickException):
    def __init__(self, error_messages: List[str], errors):
        self.error_messages = error_messages
        self.errors = errors

    def show(self):
        for error in self.error_messages:
            click.echo(error)

        for (key, error) in self.errors.items():
            click.echo('- {}: {}'.format(key, error))


class NoneAuth(AuthBase):
    """
    Creates a "None" auth type as if actual None is set as auth and a netrc
    credentials are found, python-requests will use them instead.
    """

    def __call__(self, request):
        return request


class JIRAClient(object):
    def __init__(self, base_url: str, auth=None):
        self.session = requests.Session()
        self.base_url = base_url
        self.rest_base_url = urljoin(self.base_url, 'rest/api/2/')

        if auth:
            self.session.auth = HTTPBasicAuth(auth[0], auth[1])
        else:
            self.session.auth = NoneAuth()

    # Methods

    def validate_response(self, response: requests.Response) -> None:
        if response.status_code >= 400 and 'application/json' in response.headers.get(
            'Content-Type', ''
        ):
            error = response.json()
            raise JIRAException(error.get('errorMessages', []), error.get('errors', {}))

    def get(self, path: str, **kwargs) -> requests.Response:
        url = urljoin(self.rest_base_url, path)
        response = self.session.get(url, **kwargs)
        self.validate_response(response)
        return response

    def post(self, path: str, json) -> requests.Response:
        url = urljoin(self.rest_base_url, path)
        response = self.session.post(url, json=json)
        self.validate_response(response)
        return response

    def put(self, path: str, json) -> requests.Response:
        url = urljoin(self.rest_base_url, path)
        response = self.session.put(url, json=json)
        self.validate_response(response)
        return response

    @property
    def username(self) -> Optional[str]:
        if self.session.auth and isinstance(self.session.auth, HTTPBasicAuth):
            return self.session.auth.username

        return None

    def get_user(self) -> Optional[UserDetails]:
        response = self.get('myself', allow_redirects=False)
        response.raise_for_status()
        return UserDetails.from_json(response.json())

    def get_issue(self, issue_key: str) -> Issue:
        response = self.get('issue/%s' % issue_key)
        response.raise_for_status()
        return Issue.from_json(response.json())

    def get_issue_transitions(self, issue_key: str) -> List[Transition]:
        response = self.get(
            'issue/%s/transitions' % issue_key, params={'expand': 'transitions.fields'}
        )
        response.raise_for_status()
        return list(map(Transition.from_json, response.json()['transitions']))

    def change_status(self, issue_key: str, transition_id: str) -> None:
        data = {'transition': {'id': transition_id}}
        self.post('issue/%s/transitions' % issue_key, data)

    def edit_issue(self, issue_key: str, updated_fields) -> None:
        data = {'fields': updated_fields}
        self.put('issue/%s' % issue_key, data)

    def attach(self, issue_key: str, attachment) -> List[Attachment]:
        media_type = mimetypes.guess_type(attachment.name)
        files = {
            'file': (attachment.name, attachment, media_type[0]),
        }
        url = urljoin(self.rest_base_url, f'issue/{issue_key}/attachments')
        response = self.session.post(
            url,
            headers={'X-Atlassian-Token': 'no-check'},
            files=files,
        )
        self.validate_response(response)
        return list(map(Attachment.from_json, response.json()))

    def create_issue(self, fields) -> Issue:
        response = self.post('issue', {'fields': fields})
        return Issue.from_json(response.json())

    def assign(self, issue_key: str, name: Optional[str]) -> None:
        response = self.put('issue/%s/assignee' % issue_key, {'name': name})
        response.raise_for_status()

    def comment(self, issue_key: str, comment: str) -> Comment:
        response = self.post('issue/%s/comment' % issue_key, {'body': comment})
        return Comment.from_json(response.json())

    def comments(self, issue_key: str) -> Comments:
        response = self.get('issue/%s/comment' % issue_key)
        return Comments.from_json(response.json())

    def search(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        max_results: Optional[int] = None,
        start_at: Optional[int] = None,
    ) -> SearchResults:
        body = {'jql': query}

        if start_at:
            body['startAt'] = start_at

        if max_results is not None:
            body['maxResults'] = max_results

        if fields:
            body['fields'] = fields

        response = self.post('search', body)
        response.raise_for_status()
        return SearchResults.from_json(response.json())

    def search_all(
        self,
        query: str,
        fields: Optional[List[str]] = None,
    ) -> Generator[Issue, None, None]:
        issues = 0

        while True:
            results = self.search(query, fields, start_at=issues)
            issues += len(results.issues)

            for issue in results.issues:
                yield issue

            if len(results.issues) == 0:
                break

            if issues >= results.total:
                break

        return issues

    def create_sprint(
        self,
        board_id: int,
        name: str,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
    ) -> Sprint:
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
