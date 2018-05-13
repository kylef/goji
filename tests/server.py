import unittest
import json
from threading import Thread

from six.moves import BaseHTTPServer


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
    def __init__(self, method, path, headers, body):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body


class Response(object):
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body


class JIRAServer(object):
    def __init__(self):
        self.reset()

        class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
            def do_GET(handler):
                handler.handle_request('GET')

            def do_POST(handler):
                handler.handle_request('POST')

            def do_PUT(handler):
                handler.handle_request('PUT')

            def handle_request(handler, method):
                if self.require_method and method != self.require_method:
                    raise Exception('Client called incorrect method')

                if self.require_path and handler.path != self.require_path:
                    raise Exception('Client called incorrect path: ' + handler.path)

                if 'Content-Length' in handler.headers and \
                        handler.headers['Content-Type'] == 'application/json':
                    length = int(handler.headers['Content-Length'])
                    raw_body = handler.rfile.read(length).decode('utf-8')
                    body = json.loads(raw_body)
                else:
                    body = None

                request = Request(method, handler.path, handler.headers, body)
                self.requests.append(request)

                body = json.dumps(self.response.body)

                handler.send_response(self.response.status_code)
                handler.send_header('Content-Length', str(len(body)))
                handler.send_header('Content-Type', 'application/json')
                handler.end_headers()
                handler.wfile.write(body.encode('utf-8'))

            def log_request(self, *args):
                pass

        self.server = BaseHTTPServer.HTTPServer(('localhost', 0), Handler)
        self.server.timeout = 0.5
        self.thread = Thread(target=self.server.serve_forever, args=(0.1,))
        self.thread.daemon = True
        self.thread.start()

    @property
    def address(self):
        return '{0}:{1}'.format(*self.server.server_address)

    @property
    def url(self):
        return 'http://%s' % self.address

    @property
    def last_request(self):
        return self.requests[-1]

    def reset(self):
        self.requests = []
        self.response = Response(200, None)
        self.require_method = None
        self.require_path = None

    def shutdown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def set_user_response(self):
        self.require_method = 'GET'
        self.require_path = '/rest/api/2/myself'

        self.response.status_code = 200
        self.response.body = {
            'name': 'kyle',
            'displayName': 'Kyle Fuller',
            'emailAddress': 'kyle@example.com',
        }
