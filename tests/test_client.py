import unittest
import datetime

from goji.client import JIRAClient, JIRAException

from tests.server import JIRAServer


class ClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = JIRAServer()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        self.client = JIRAClient(self.server.url)

    def test_post_400_error(self):
        self.server.response.status_code = 400
        self.server.response.body = {
            'errorMessages': ['Big Problem']
        }

        with self.assertRaises(JIRAException):
            self.client.post('path', {
                'body': 'example',
            })

    def test_get_user(self):
        self.server.response.body = {
            'name': 'kyle',
            'displayName': 'Kyle Fuller',
            'emailAddress': 'kyle@example.com',
        }
        user = self.client.get_user()

        self.assertEqual(user.username, 'kyle')
        self.assertEqual(user.name, 'Kyle Fuller')
        self.assertEqual(user.email, 'kyle@example.com')

        self.assertEqual(self.server.last_request.method, 'GET')
        self.assertEqual(self.server.last_request.path, '/rest/api/2/myself')

    def test_get_issue(self):
        self.server.response.body = {
            'key': 'GOJI-13',
            'fields': {
                'summary': 'Implement Client Unit Tests',
                'status': {
                    'name': 'open',
                }
            },
        }
        issue = self.client.get_issue('GOJI-13')

        self.assertEqual(issue.summary, 'Implement Client Unit Tests')

        self.assertEqual(self.server.last_request.method, 'GET')
        self.assertEqual(self.server.last_request.path, '/rest/api/2/issue/GOJI-13')

    def test_create_issue(self):
        self.server.response.body = {
            'key': 'GOJI-14',
        }

        self.client.create_issue({
            'summary': 'Test Creating Issues in JIRA Client',
        })

        self.assertEqual(self.server.last_request.method, 'POST')
        self.assertEqual(self.server.last_request.path, '/rest/api/2/issue')
        self.assertEqual(self.server.last_request.body, {
            'fields': {
                'summary': 'Test Creating Issues in JIRA Client',
            }
        })

    def test_edit_issue(self):
        self.client.edit_issue('GOJI-15', {
            'summary': 'Test Updating Issues in JIRA Client',
        })

        self.assertEqual(self.server.last_request.method, 'PUT')
        self.assertEqual(self.server.last_request.path, '/rest/api/2/issue/GOJI-15')
        self.assertEqual(self.server.last_request.body, {
            'fields': {
                'summary': 'Test Updating Issues in JIRA Client',
            }
        })

    def test_comment(self):
        self.server.response.body = {
            'key': 'GOJI-14',
        }

        self.client.comment('GOJI-14', 'Hello World')

        self.assertEqual(self.server.last_request.method, 'POST')
        self.assertEqual(self.server.last_request.path,
            '/rest/api/2/issue/GOJI-14/comment')
        self.assertEqual(self.server.last_request.body, {
            'body': 'Hello World'
        })

    def test_create_sprint(self):
        self.server.response.status_code = 201

        self.client.create_sprint(5, 'Testing Sprint #1')

        self.assertEqual(self.server.last_request.path, '/rest/agile/1.0/sprint')
        self.assertEqual(self.server.last_request.body, {
            'name': 'Testing Sprint #1',
            'originBoardId': 5,
        })

    def test_create_sprint_start_end(self):
        self.server.response.status_code = 201

        self.client.create_sprint(5, 'Testing Sprint #1',
            datetime.datetime(2018, 1, 1), datetime.datetime(2018, 6, 1))

        self.assertEqual(self.server.last_request.method, 'POST')
        self.assertEqual(self.server.last_request.path, '/rest/agile/1.0/sprint')
        self.assertEqual(self.server.last_request.body, {
            'name': 'Testing Sprint #1',
            'originBoardId': 5,
            'startDate': '2018-01-01T00:00:00',
            'endDate': '2018-06-01T00:00:00',
        })
