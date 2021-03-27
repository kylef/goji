import unittest
from typing import List

from click.testing import CliRunner

from goji.commands import cli
from goji.models import Transition


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
