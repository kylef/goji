import unittest
from typing import List

from click.testing import CliRunner

from goji.commands import cli
from goji.models import Transition
from tests.server import OPEN_STATUS, JIRAServer


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


def test_change_status_invalid_issue_key(invoke, server: JIRAServer) -> None:
    server.set_transition_response('GOJI-15', [])
    result = invoke('change-status', 'GOJI-15')

    assert (
        result.output
        == 'Fetching possible transitions...\nNo transitions found for GOJI-15\n'
    )
    assert result.exception is None
    assert result.exit_code == 0


def test_change_status_valid_issue_key_invalid_input(
    invoke, server: JIRAServer
) -> None:
    server.set_transition_response(
        'GOJI-15',
        [
            {'id': '31', 'name': 'Unstarted'},
            {'id': '21', 'name': 'Going'},
            {'id': '1', 'name': 'Done'},
        ],
    )

    result = invoke('change-status', 'GOJI-15', input='3\n')
    assert (
        result.output
        == 'Fetching possible transitions...\n0: Unstarted\n1: Going\n2: Done\nSelect a transition: 3\nNo transitions match "3"\n'
    )
    assert result.exception is None
    assert result.exit_code == 0


def test_change_status_valid_issue_key_valid_input(invoke, server: JIRAServer) -> None:
    server.set_transition_response(
        'GOJI-15',
        [
            {'id': '31', 'name': 'Unstarted', 'statusCategory': OPEN_STATUS},
            {'id': '21', 'name': 'Going', 'statusCategory': OPEN_STATUS},
            {'id': '1', 'name': 'Done', 'statusCategory': OPEN_STATUS},
        ],
    )

    def on_request() -> None:
        server.set_perform_transition_response('GOJI-15')

    setattr(server, 'got_request', on_request)

    result = invoke('change-status', 'GOJI-15', input='1\n')
    assert (
        result.output
        == 'Fetching possible transitions...\n0: Unstarted\n1: Going\n2: Done\nSelect a transition: 1\nOkay, the status for GOJI-15 is now "Going".\n'
    )
    assert result.exception is None
    assert result.exit_code == 0


def test_change_status_specify_invalid_status_name(invoke, server: JIRAServer) -> None:
    server.set_transition_response(
        'GOJI-15',
        [
            {'id': '31', 'name': 'Unstarted'},
            {'id': '21', 'name': 'Going'},
            {'id': '1', 'name': 'Done'},
        ],
    )
    result = invoke('change-status', 'GOJI-15', 'foo')

    assert (
        result.output
        == 'Fetching possible transitions...\nNo transitions match "foo"\n'
    )
    assert result.exception is None
    assert result.exit_code == 0


def test_change_status_specify_valid_status_name(invoke, server: JIRAServer) -> None:
    server.set_transition_response(
        'GOJI-15',
        [
            {'id': '31', 'name': 'Unstarted'},
            {'id': '21', 'name': 'Going'},
            {'id': '1', 'name': 'Done'},
        ],
    )

    def on_request() -> None:
        server.set_perform_transition_response('GOJI-15')

    setattr(server, 'got_request', on_request)

    result = invoke('change-status', 'GOJI-15', 'done')
    assert (
        result.output
        == 'Fetching possible transitions...\nOkay, the status for GOJI-15 is now "Done".\n'
    )
    assert result.exception is None
    assert result.exit_code == 0
