import unittest
import os

from click.testing import CliRunner

from goji.commands import cli
from goji.models import Issue


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
