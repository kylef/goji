import os
import unittest
from typing import List

from click.testing import CliRunner

from goji.client import JIRAClient
from goji.commands import cli
from goji.models import Transition
from tests.server import ServerTestCase


class TestClient(object):
    base_url = 'https://goji.example.com/'
    username = 'kyle'

    def get_issue_transitions(self, issue_key: str) -> List[Transition]:
        if issue_key == 'invalid':
            return []
        else:
            return [
                Transition('31', 'Unstarted'),
                Transition('21', 'Going'),
                Transition('1', 'Done'),
            ]

    def change_status(self, issue_key: str, transition_id: str) -> None:
        pass


class CommandTestCase(ServerTestCase):
    def setUp(self) -> None:
        super(CommandTestCase, self).setUp()
        self.runner = CliRunner()

    def invoke(self, *args, **kwargs):
        args = ['--base-url', self.server.url] + list(args)

        if 'client' in kwargs:
            client = kwargs.pop('client')
        else:
            client = JIRAClient(self.server.url, ('kyle', None))

        result = self.runner.invoke(cli, args, obj=client, **kwargs)
        return result


class CLITests(CommandTestCase):
    def test_error_without_base_url(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ['open'])

        assert "Error: Missing option '--base-url'" in result.output
        assert result.exit_code != 0

    def test_providing_no_credentials(self) -> None:
        result = self.invoke('whoami', client=None)

        self.assertEqual(
            result.output, 'Error: Authentication not configured. Run `goji login`.\n'
        )
        assert result.exit_code == 1

    def test_providing_email_password(self):
        self.server.set_user_response()

        result = self.invoke(
            '--email', 'kyle@example.com', '--password', 'pass', 'whoami', client=None
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Kyle Fuller (kyle)\n')
        self.assertEqual(result.exit_code, 0)

    def test_providing_email_no_password(self):
        self.server.set_user_response()

        result = self.invoke('--email', 'kyle@example.com', 'whoami', client=None)

        self.assertEqual(
            result.output, 'Error: Email/password must be provided together.\n'
        )
        self.assertEqual(result.exit_code, 1)

    def test_providing_password_no_email(self):
        self.server.set_user_response()

        result = self.invoke('--password', 'pass', 'whoami', client=None)

        self.assertEqual(
            result.output, 'Error: Email/password must be provided together.\n'
        )
        self.assertEqual(result.exit_code, 1)


class LoginCommandTests(CommandTestCase):
    def test_login(self):
        self.server.set_user_response()

        with self.runner.isolated_filesystem():
            result = self.invoke('login', client=None, input='email\npassword\n')

            with open(os.path.expanduser('~/.netrc')) as fp:
                self.assertEqual(
                    fp.read(), 'machine 127.0.0.1\n  login email\n  password password'
                )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            self.server.last_request.headers['Authorization'],
            'Basic ZW1haWw6cGFzc3dvcmQ=',
        )

    def test_login_incorret_credentials(self):
        self.server.set_error_response(401, 'Authorization')
        self.server.response.headers['Content-Type'] = 'text/plain'

        result = self.invoke('login', client=None, input='email\npassword\n')

        self.assertTrue(
            'Error: Incorrect credentials. Try `goji login`.' in result.output
        )
        self.assertEqual(result.exit_code, 1)


class ShowCommandTests(CommandTestCase):
    def test_show__without_issue_key(self) -> None:
        result = self.invoke('show')

        assert "Error: Missing argument 'ISSUE_KEY'" in result.output
        self.assertNotEqual(result.exit_code, 0)

    def test_show_with_issue_key(self):
        self.server.set_issue_response()

        result = self.invoke('show', 'GOJI-1')
        output = result.output.replace(self.server.url, 'https://example.com')

        expected = '''-> GOJI-1
  Example Issue

  Issue Description

  - Status: Open
  - Creator: Kyle Fuller (kyle)
  - Assigned: Delisa (delisa)
  - URL: https://example.com/browse/GOJI-1
'''

        assert output == expected
        assert result.exit_code == 0


class AssignCommandTests(CommandTestCase):
    def test_assign_specified_user(self):
        self.server.set_assign_response('GOJI-123')

        result = self.invoke('assign', 'GOJI-123', 'jones')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'GOJI-123 has been assigned to jones.\n')
        self.assertEqual(result.exit_code, 0)

        self.assertEqual(self.server.last_request.body, {'name': 'jones'})

    def test_assign_current_user(self):
        self.server.set_assign_response('GOJI-123')

        result = self.invoke('assign', 'GOJI-123')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'GOJI-123 has been assigned to kyle.\n')
        self.assertEqual(result.exit_code, 0)

        self.assertEqual(self.server.last_request.body, {'name': 'kyle'})


class UnassignCommandTests(CommandTestCase):
    def test_unassign(self):
        self.server.set_assign_response('GOJI-123')

        result = self.invoke('unassign', 'GOJI-123')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'GOJI-123 has been unassigned.\n')
        self.assertEqual(result.exit_code, 0)

        self.assertEqual(self.server.last_request.body, {'name': None})


class WhoamiCommandTests(CommandTestCase):
    def test_whoami(self):
        self.server.set_user_response()

        result = self.invoke('whoami')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Kyle Fuller (kyle)\n')
        self.assertEqual(result.exit_code, 0)


class ChangeStatusCommandTests(unittest.TestCase):
    def test_change_status_invalid_issue_key(self):
        runner = CliRunner()
        args = ['--base-url=https://example.com', 'change-status', 'invalid']
        result = runner.invoke(cli, args, obj=TestClient())
        self.assertIsNone(result.exception)
        self.assertEqual(
            result.output,
            'Fetching possible transitions...\nNo transitions found for invalid\n',
        )

    def test_change_status_valid_issue_key_invalid_input(self):
        runner = CliRunner()
        args = ['--base-url=https://example.com', 'change-status', 'GOJI-311']
        result = runner.invoke(cli, args, obj=TestClient(), input='3\n')
        self.assertIsNone(result.exception)
        self.assertEqual(
            result.output,
            'Fetching possible transitions...\n0: Unstarted\n1: Going\n2: Done\nSelect a transition: 3\nNo transitions match "3"\n',
        )

    def test_change_status_valid_issue_key_valid_input(self):
        runner = CliRunner()
        args = ['--base-url=https://example.com', 'change-status', 'GOJI-311']
        result = runner.invoke(cli, args, obj=TestClient(), input='1\n')
        self.assertIsNone(result.exception)
        self.assertEqual(
            result.output,
            'Fetching possible transitions...\n0: Unstarted\n1: Going\n2: Done\nSelect a transition: 1\nOkay, the status for GOJI-311 is now "Going".\n',
        )

    def test_change_status_specify_invalid_status_name(self):
        runner = CliRunner()
        args = ['--base-url=https://example.com', 'change-status', 'GOJI-311', 'foo']
        result = runner.invoke(cli, args, obj=TestClient())
        self.assertIsNone(result.exception)
        self.assertEqual(
            result.output,
            'Fetching possible transitions...\nNo transitions match "foo"\n',
        )

    def test_change_status_specify_valid_status_name(self):
        runner = CliRunner()
        args = ['--base-url=https://example.com', 'change-status', 'GOJI-311', 'done']
        result = runner.invoke(cli, args, obj=TestClient())
        self.assertIsNone(result.exception)
        self.assertEqual(
            result.output,
            'Fetching possible transitions...\nOkay, the status for GOJI-311 is now "Done".\n',
        )


class SearchCommandTests(CommandTestCase):
    def test_search(self):
        self.server.set_search_response()

        result = self.invoke('search', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'GOJI-7 My First Issue\n')
        self.assertEqual(result.exit_code, 0)

    def test_search_format_key(self):
        self.server.set_search_response()

        result = self.invoke('search', '--format', '{key}', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'GOJI-7\n')
        self.assertEqual(result.exit_code, 0)

    def test_search_format_summary(self):
        self.server.set_search_response()

        result = self.invoke('search', '--format', '{summary}', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'My First Issue\n')
        self.assertEqual(result.exit_code, 0)

    def test_search_format_description(self):
        self.server.set_search_response()

        result = self.invoke('search', '--format', '{description}', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'One\nTwo\nThree\n\n')
        self.assertEqual(result.exit_code, 0)

    def test_search_format_creator(self):
        self.server.set_search_response()

        result = self.invoke('search', '--format', '{creator}', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Kyle Fuller (kyle)\n')
        self.assertEqual(result.exit_code, 0)

    def test_search_format_assignee(self):
        self.server.set_search_response()

        result = self.invoke('search', '--format', '{assignee}', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Delisa (delisa)\n')
        self.assertEqual(result.exit_code, 0)


class CommentCommandTests(CommandTestCase):
    def test_commenting_with_message(self):
        self.server.set_comment_response('GOJI-311')

        result = self.invoke('comment', 'GOJI-311', '-m', 'My short one-line comment')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Comment created\n')
        self.assertEqual(result.exit_code, 0)

    def test_commenting_producing_error(self):
        self.server.set_error_response(404, 'Issue Does Not Exist')

        result = self.invoke('comment', 'GOJI-311', '-m', 'My short one-line comment')

        self.assertEqual(
            result.output,
            'Comment:\n\nMy short one-line comment\n\nIssue Does Not Exist\n',
        )
        self.assertEqual(result.exit_code, 1)


class NewCommandTests(CommandTestCase):
    def test_create_issue_error(self):
        self.server.set_error_response(400, "Field 'priority' is required")

        result = self.invoke('create', 'GOJI', 'Sprint #1', '--description', 'Desc')

        self.assertEqual(
            result.output, "Description:\n\nDesc\n\nField 'priority' is required\n"
        )
        self.assertEqual(result.exit_code, 1)

    def test_new_title_description(self):
        self.server.set_create_issue_response()

        result = self.invoke('create', 'GOJI', 'Sprint #1', '--description', 'Desc')

        self.assertEqual(
            self.server.last_request.body,
            {
                'fields': {
                    'description': 'Desc',
                    'project': {'key': 'GOJI'},
                    'summary': 'Sprint #1',
                }
            },
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Issue GOJI-133 created\n')
        self.assertEqual(result.exit_code, 0)

    def test_new_specify_component(self):
        self.server.set_create_issue_response()

        result = self.invoke(
            'create',
            'GOJI',
            'Sprint #1',
            '--component',
            'client',
            '-c',
            'api',
            '--description',
            'Desc',
        )

        self.assertEqual(
            self.server.last_request.body,
            {
                'fields': {
                    'description': 'Desc',
                    'project': {'key': 'GOJI'},
                    'summary': 'Sprint #1',
                    'components': [{'name': 'client'}, {'name': 'api'}],
                }
            },
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Issue GOJI-133 created\n')
        self.assertEqual(result.exit_code, 0)

    def test_new_specify_label(self):
        self.server.set_create_issue_response()

        result = self.invoke(
            'create',
            'GOJI',
            'Sprint #1',
            '--label',
            'api',
            '--label',
            'cli',
            '--description',
            'Desc',
        )

        self.assertEqual(
            self.server.last_request.body,
            {
                'fields': {
                    'description': 'Desc',
                    'project': {'key': 'GOJI'},
                    'summary': 'Sprint #1',
                    'labels': ['api', 'cli'],
                }
            },
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Issue GOJI-133 created\n')
        self.assertEqual(result.exit_code, 0)

    def test_new_specify_type(self):
        self.server.set_create_issue_response()

        result = self.invoke(
            'create', 'GOJI', 'Sprint #1', '--type', 'Bug', '--description', 'Desc'
        )

        self.assertEqual(
            self.server.last_request.body,
            {
                'fields': {
                    'description': 'Desc',
                    'issuetype': {'name': 'Bug'},
                    'project': {'key': 'GOJI'},
                    'summary': 'Sprint #1',
                }
            },
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Issue GOJI-133 created\n')
        self.assertEqual(result.exit_code, 0)

    def test_new_specify_priority(self):
        self.server.set_create_issue_response()

        result = self.invoke(
            'create', 'GOJI', 'Sprint #1', '--priority', 'hot', '--description', 'Desc'
        )

        self.assertEqual(
            self.server.last_request.body,
            {
                'fields': {
                    'description': 'Desc',
                    'project': {'key': 'GOJI'},
                    'priority': {'name': 'hot'},
                    'summary': 'Sprint #1',
                }
            },
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Issue GOJI-133 created\n')
        self.assertEqual(result.exit_code, 0)


class CreateSprintTests(CommandTestCase):
    def test_creating_sprint(self):
        self.server.set_create_sprint_response()

        result = self.invoke('sprint', 'create', '1', 'Sprint #1')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Sprint created\n')
        self.assertEqual(result.exit_code, 0)

    def test_creating_sprint_with_date(self):
        self.server.set_create_sprint_response()

        result = self.invoke(
            'sprint',
            'create',
            '1',
            'Sprint #1',
            '--start',
            '10/01/18',
            '--end',
            '20/01/18',
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Sprint created\n')
        self.assertEqual(result.exit_code, 0)

    def test_creating_sprint_with_invalid_date(self):
        self.server.set_create_sprint_response()

        result = self.invoke(
            'sprint',
            'create',
            '1',
            'Sprint #1',
            '--start',
            '10/13/18',
            '--end',
            '20/01/18',
        )

        self.assertEqual(result.exit_code, 2)
