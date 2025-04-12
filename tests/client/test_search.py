from goji.client import JIRAClient
from tests.server import OPEN_STATUS, JIRAServer, Response


def test_search(client: JIRAClient, server: JIRAServer):
    server.response.body = {
        'issues': [
            {
                'key': 'GOJI-1',
                'fields': {
                    'summary': 'Hello World',
                    'description': 'One\nTwo\nThree\n',
                    'status': OPEN_STATUS,
                },
            }
        ],
        'startAt': 0,
        'maxResults': 50,
        'total': 1,
    }

    results = client.search('PROJECT = GOJI')

    assert server.last_request.method == 'POST'
    assert server.last_request.path == '/rest/api/2/search'
    assert server.last_request.body == {'jql': 'PROJECT = GOJI'}

    assert len(results.issues) == 1
    assert results.issues[0].key == 'GOJI-1'


def test_search_all_single_page(client: JIRAClient, server: JIRAServer):
    server.response.body = {
        'issues': [
            {
                'key': 'GOJI-1',
                'fields': {
                    'summary': 'Hello World',
                    'description': 'One\nTwo\nThree\n',
                    'status': OPEN_STATUS,
                },
            }
        ],
        'startAt': 0,
        'maxResults': 50,
        'total': 1,
    }

    issues = list(client.search_all('PROJECT = GOJI'))

    assert server.last_request.method == 'POST'
    assert server.last_request.path == '/rest/api/2/search'
    assert server.last_request.body == {'jql': 'PROJECT = GOJI'}

    assert len(issues) == 1
    assert issues[0].key == 'GOJI-1'


def test_search_all_two_page(client: JIRAClient, server: JIRAServer):
    server.response = None
    server.responses = [
        Response(
            200,
            {
                'issues': [
                    {
                        'key': 'GOJI-1',
                        'fields': {
                            'summary': 'Hello World',
                            'description': 'One\nTwo\nThree\n',
                            'status': OPEN_STATUS,
                        },
                    }
                ],
                'startAt': 0,
                'maxResults': 1,
                'total': 2,
            },
        ),
        Response(
            200,
            {
                'issues': [
                    {
                        'key': 'GOJI-2',
                        'fields': {
                            'summary': 'Hello World',
                            'description': 'One\nTwo\nThree\n',
                            'status': OPEN_STATUS,
                        },
                    }
                ],
                'startAt': 1,
                'maxResults': 1,
                'total': 2,
            },
        ),
    ]

    issues = list(client.search_all('PROJECT = GOJI'))
    assert len(issues) == 2

    assert len(server.requests) == 2
    assert server.requests[0].body == {'jql': 'PROJECT = GOJI'}
    assert server.requests[1].body == {'jql': 'PROJECT = GOJI', 'startAt': 1}
