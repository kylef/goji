import unittest
import os

from click.testing import CliRunner

from goji.commands import cli
from goji.models import Issue, Transition


class TestClient(object):
    base_url = 'https://goji.example.com/'

    def __init__(self):
        pass

    def get_issue(self, issue_key):
        issue = Issue(issue_key)
        issue.summary = 'Example issue'
        issue.description = None
        issue.status = 'Open'
        issue.creator = 'kyle'
        issue.assignee = 'kyle'
        issue.links = []
        return issue

    def get_issue_transitions(self, issue_key):
        if issue_key == 'invalid':
            return []
        else:
            return [Transition('31', 'Unstarted'),
                    Transition('21', 'Going'),
                    Transition('1', 'Done')]

    def change_status(self, issue_key, transition_id):
        return True


class CLITests(unittest.TestCase):
    def test_error_without_base_url(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['open'])

        self.assertTrue('Error: Missing option "--base-url"' in result.output)
        self.assertNotEqual(result.exit_code, 0)


class ShowCommandTests(unittest.TestCase):
    def test_show__without_issue_key(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--base-url=https://example.com', 'show'], obj=TestClient())

        self.assertTrue('Error: Missing argument "issue_key"' in result.output)
        self.assertNotEqual(result.exit_code, 0)

    def test_show_with_issue_key(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--base-url=https://example.com', 'show', 'XX-123'], obj=TestClient())

        self.assertEqual(result.output, '-> XX-123\n  Example issue\n\n  - Status: Open\n  - Creator: kyle\n  - Assigned: kyle\n  - URL: https://goji.example.com/browse/XX-123\n')
        self.assertEqual(result.exit_code, 0)

class ChangeStatusCommandTests(unittest.TestCase):
    def test_change_status_invalid_issue_key(self):
        runner = CliRunner()
        args = ['--base-url=https://example.com', 'change-status', 'invalid']
        result = runner.invoke(cli, args, obj=TestClient())
        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Fetching possible transitions...\nNo transitions found for invalid\n')

    def test_change_status_valid_issue_key_invalid_input(self):
        runner = CliRunner()
        args = ['--base-url=https://example.com', 'change-status', 'GOJI-311']
        result = runner.invoke(cli, args, obj=TestClient(), input='3\n')
        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Fetching possible transitions...\n0: Unstarted\n1: Going\n2: Done\nSelect a transition: 3\nNo transitions match "3"\n')

    def test_change_status_valid_issue_key_valid_input(self):
        runner = CliRunner()
        args = ['--base-url=https://example.com', 'change-status', 'GOJI-311']
        result = runner.invoke(cli, args, obj=TestClient(), input='1\n')
        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Fetching possible transitions...\n0: Unstarted\n1: Going\n2: Done\nSelect a transition: 1\nOkay, the status for GOJI-311 is now "Going".\n')
