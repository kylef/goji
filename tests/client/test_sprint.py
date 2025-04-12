import datetime

from goji.client import JIRAClient
from tests.server import JIRAServer


def test_create_sprint(client: JIRAClient, server: JIRAServer):
    server.response.status_code = 201
    server.response.body = {
        'id': 12,
        'name': 'Testing Sprint #1',
        'state': 'future',
    }

    sprint = client.create_sprint(5, 'Testing Sprint #1')

    assert server.last_request.path == '/rest/agile/1.0/sprint'
    assert server.last_request.body == {
        'name': 'Testing Sprint #1',
        'originBoardId': 5,
    }


def test_create_sprint_start_end(client: JIRAClient, server: JIRAServer):
    server.response.status_code = 201
    server.response.body = {
        'id': 12,
        'name': 'Testing Sprint #1',
        'state': 'future',
    }

    sprint = client.create_sprint(
        5,
        'Testing Sprint #1',
        datetime.datetime(2018, 1, 1),
        datetime.datetime(2018, 6, 1),
    )

    assert server.last_request.method == 'POST'
    assert server.last_request.path == '/rest/agile/1.0/sprint'
    assert server.last_request.body == {
        'name': 'Testing Sprint #1',
        'originBoardId': 5,
        'startDate': '2018-01-01T00:00:00',
        'endDate': '2018-06-01T00:00:00',
    }
