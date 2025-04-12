import datetime

import pytest

from goji.client import JIRAClient, JIRAException
from tests.server import OPEN_STATUS, JIRAServer, Response


def test_post_400_error(client: JIRAClient, server: JIRAServer):
    server.response.status_code = 400
    server.response.body = {'errorMessages': ['Big Problem']}

    with pytest.raises(JIRAException):
        client.post(
            'path',
            {
                'body': 'example',
            },
        )


def test_post_404_error(client: JIRAClient, server: JIRAServer):
    server.response.status_code = 404
    server.response.body = {
        'errors': {
            'rapidViewId': 'The requested board cannot be viewed because it either does not exist or you do not have permission to view it.'
        }
    }

    with pytest.raises(JIRAException):
        client.post(
            'path',
            {
                'body': 'example',
            },
        )


def test_basic_authentication(client: JIRAClient, server: JIRAServer):
    server.response.body = {
        'name': 'kyle',
        'displayName': 'Kyle Fuller',
        'emailAddress': 'kyle@example.com',
    }

    client.get_user()

    assert server.last_request.method == 'GET'
    assert server.last_request.path == '/rest/api/2/myself'
    assert (
        server.last_request.headers.get('Authorization')
        == 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='
    )


def test_get_user(client: JIRAClient, server: JIRAServer):
    server.response.body = {
        'name': 'kyle',
        'displayName': 'Kyle Fuller',
        'emailAddress': 'kyle@example.com',
    }
    user = client.get_user()

    assert user.username == 'kyle'
    assert user.name == 'Kyle Fuller'
    assert user.email == 'kyle@example.com'

    assert server.last_request.method == 'GET'
    assert server.last_request.path == '/rest/api/2/myself'


def test_get_issue(client: JIRAClient, server: JIRAServer):
    server.response.body = {
        'key': 'GOJI-13',
        'fields': {
            'summary': 'Implement Client Unit Tests',
            'status': OPEN_STATUS,
        },
    }
    issue = client.get_issue('GOJI-13')

    assert issue.summary == 'Implement Client Unit Tests'

    assert server.last_request.method == 'GET'
    assert server.last_request.path == '/rest/api/2/issue/GOJI-13'


def test_get_issue_transitions(client: JIRAClient, server: JIRAServer):
    server.response.body = {'transitions': [{'id': 1, 'name': 'Close Issue'}]}

    transitions = client.get_issue_transitions('GOJI-13')

    assert len(transitions) == 1
    assert transitions[0].id == 1
    assert transitions[0].name == 'Close Issue'

    assert server.last_request.method == 'GET'
    assert (
        server.last_request.path
        == '/rest/api/2/issue/GOJI-13/transitions?expand=transitions.fields'
    )


def test_transition_issue(client: JIRAClient, server: JIRAServer):
    server.response.status_code = 204

    client.change_status('GOJI-14', 1)

    assert server.last_request.method == 'POST'
    assert server.last_request.path == '/rest/api/2/issue/GOJI-14/transitions'
    assert server.last_request.body == {'transition': {'id': 1}}


def test_create_issue(client: JIRAClient, server: JIRAServer):
    server.response.status_code = 201
    server.response.body = {
        'id': '10000',
        'key': 'GOJI-14',
    }

    issue = client.create_issue(
        {
            'summary': 'Test Creating Issues in JIRA Client',
        }
    )

    assert issue.key == 'GOJI-14'

    assert server.last_request.method == 'POST'
    assert server.last_request.path == '/rest/api/2/issue'
    assert server.last_request.body == {
        'fields': {
            'summary': 'Test Creating Issues in JIRA Client',
        }
    }


def test_edit_issue(client: JIRAClient, server: JIRAServer):
    client.edit_issue(
        'GOJI-15',
        {
            'summary': 'Test Updating Issues in JIRA Client',
        },
    )

    assert server.last_request.method == 'PUT'
    assert server.last_request.path == '/rest/api/2/issue/GOJI-15'
    assert server.last_request.body == {
        'fields': {
            'summary': 'Test Updating Issues in JIRA Client',
        }
    }


def test_assign(client: JIRAClient, server: JIRAServer):
    server.response.status_code = 204

    client.assign('GOJI-14', 'kyle')

    assert server.last_request.method == 'PUT'
    assert server.last_request.path == '/rest/api/2/issue/GOJI-14/assignee'
    assert server.last_request.body == {'name': 'kyle'}


def test_comment(client: JIRAClient, server: JIRAServer):
    server.response.body = {
        'id': '10000',
        'author': {
            'name': 'fred',
            'displayName': 'Fred F. User',
        },
        'body': 'Hello World',
        'created': '2018-05-08T05:54:42.688+0000',
    }

    comment = client.comment('GOJI-14', 'Hello World')

    assert comment.body == 'Hello World'
    assert comment.author.name == 'Fred F. User'

    assert server.last_request.method == 'POST'
    assert server.last_request.path == '/rest/api/2/issue/GOJI-14/comment'
    assert server.last_request.body == {'body': 'Hello World'}
