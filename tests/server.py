import json
import unittest
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from typing import Any, Dict, List, Optional

OPEN_STATUS = {
    'id': 1,
    'name': 'Open',
    'statusCategory': {
        'id': 'a',
        'key': 'a',
        'name': 'c',
    },
}


class ServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = JIRAServer()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        self.server.reset()


class Request(object):
    def __init__(self, method: str, path: str, headers, body):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body


class Response(object):
    def __init__(self, status_code: int, body):
        self.status_code = status_code
        self.headers = {'Content-Type': 'application/json'}
        self.body = body


class JIRAServer(object):
    def __init__(self):
        self.reset()

        server = self

        class Handler(SimpleHTTPRequestHandler):
            def do_GET(self):
                self.handle_request('GET')

            def do_POST(self):
                self.handle_request('POST')

            def do_PUT(self):
                self.handle_request('PUT')

            def handle_request(self, method):
                if server.require_method and method != server.require_method:
                    raise Exception('Client called incorrect method')

                if server.require_path and self.path != server.require_path:
                    raise Exception('Client called incorrect path: ' + self.path)

                if (
                    'Content-Length' in self.headers
                    and self.headers['Content-Type'] == 'application/json'
                ):
                    length = int(self.headers['Content-Length'])
                    raw_body = self.rfile.read(length).decode('utf-8')
                    body = json.loads(raw_body)
                else:
                    body = None

                request = Request(method, self.path, self.headers, body)
                server.requests.append(request)

                body = json.dumps(server.response.body)

                self.send_response(server.response.status_code)
                self.send_header('Content-Length', str(len(body)))
                self.send_header(
                    'Content-Type', server.response.headers['Content-Type']
                )
                self.end_headers()
                self.wfile.write(body.encode('utf-8'))

                server.got_request()

            def log_request(self, *args):
                pass

        self.server = HTTPServer(('localhost', 0), Handler)
        self.server.timeout = 0.5
        self.thread = Thread(target=self.server.serve_forever, args=(0.1,))
        self.thread.daemon = True
        self.thread.start()

    def got_request(self) -> None:
        pass

    @property
    def address(self) -> str:
        return '{0}:{1}'.format(*self.server.server_address)

    @property
    def url(self) -> str:
        return 'http://%s' % self.address

    @property
    def last_request(self) -> Request:
        return self.requests[-1]

    def reset(self) -> None:
        self.requests: List[Request] = []
        self.response = Response(200, None)
        self.require_method: Optional[str] = None
        self.require_path: Optional[str] = None

    def shutdown(self) -> None:
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def set_error_response(self, status_code: int, error: str) -> None:
        self.response.status_code = status_code
        self.response.body = {'errorMessages': [error]}

    def set_user_response(self) -> None:
        self.require_method = 'GET'
        self.require_path = '/rest/api/2/myself'

        self.response.status_code = 200
        self.response.body = {
            'name': 'kyle',
            'displayName': 'Kyle Fuller',
            'emailAddress': 'kyle@example.com',
        }

    def set_issue_response(self, issue_key: str = 'GOJI-1') -> None:
        self.require_method = 'GET'
        self.require_path = '/rest/api/2/issue/{}'.format(issue_key)

        self.response.status_code = 200
        self.response.body = {
            'key': issue_key,
            'fields': {
                'summary': 'Example Issue',
                'description': 'Issue Description',
                'status': OPEN_STATUS,
                'creator': {'displayName': 'Kyle Fuller', 'name': 'kyle'},
                'assignee': {'displayName': 'Delisa', 'name': 'delisa'},
            },
        }

    def set_create_issue_response(self) -> None:
        self.require_method = 'POST'
        self.require_path = '/rest/api/2/issue'

        self.response.status_code = 200
        self.response.body = {
            'key': 'GOJI-133',
            'fields': {
                'summary': 'Example Issue',
                'description': 'Issue Description',
                'status': OPEN_STATUS,
                'creator': {'displayName': 'Kyle Fuller', 'name': 'kyle'},
                'assignee': {'displayName': 'Delisa', 'name': 'delisa'},
            },
        }

    def set_assign_response(self, issue_key: str) -> None:
        self.require_method = 'PUT'
        self.require_path = '/rest/api/2/issue/{}/assignee'.format(issue_key)

        self.response.status_code = 204

    def set_transition_response(
        self, issue_key: str, transitions: List[Dict[str, Any]]
    ) -> None:
        self.require_method = 'GET'
        self.require_path = (
            '/rest/api/2/issue/{}/transitions?expand=transitions.fields'.format(
                issue_key
            )
        )

        self.response.status_code = 200
        self.response.body = {'transitions': transitions}

    def set_perform_transition_response(self, issue_key: str) -> None:
        self.require_method = 'POST'
        self.require_path = '/rest/api/2/issue/{}/transitions'.format(issue_key)

        self.response.status_code = 200

    def set_comment_response(self, issue_key: str) -> None:
        self.require_method = 'POST'
        self.require_path = '/rest/api/2/issue/{}/comment'.format(issue_key)

        self.response.status_code = 201
        self.response.body = {
            'id': '10000',
            'author': {
                'name': 'fred',
                'displayName': 'Fred F. User',
            },
            'body': 'Hello World',
            'created': '2018-05-08T05:54:42.688+0000',
        }

    def set_search_response(self) -> None:
        self.require_method = 'POST'
        self.require_path = '/rest/api/2/search'

        self.response.status_code = 200
        self.response.body = {
            'total': 1,
            'expand': 'summary',
            'startAt': 0,
            'maxResults': 50,
            'issues': [
                {
                    'key': 'GOJI-7',
                    'fields': {
                        'summary': 'My First Issue',
                        'description': 'One\nTwo\nThree\n',
                        'status': OPEN_STATUS,
                        'creator': {'displayName': 'Kyle Fuller', 'name': 'kyle'},
                        'assignee': {'displayName': 'Delisa', 'name': 'delisa'},
                    },
                }
            ],
        }

    def set_create_sprint_response(self) -> None:
        self.require_method = 'POST'
        self.require_path = '/rest/agile/1.0/sprint'

        self.response.status_code = 201
        self.response.body = {
            'id': 12,
            'name': 'Sprint #1',
            'state': 'future',
        }
