from tests.server import JIRAServer


def test_edit_no_change(invoke, server: JIRAServer) -> None:
    server.set_issue_response()

    result = invoke('edit', 'GOJI-1', '--description', 'Issue Description')

    assert result.output == ''
    assert result.exit_code == 0


def test_edit_summary(invoke, server: JIRAServer) -> None:
    server.set_issue_response()
    server.require_method = None

    result = invoke(
        'edit', 'GOJI-1', '--summary', 'new summary', '--description', 'new description'
    )

    assert result.output == 'GOJI-1 updated.\n'
    assert result.exit_code == 0

    assert server.last_request.method == 'PUT'
    assert server.last_request.body == {
        'fields': {
            'summary': 'new summary',
            'description': 'new description',
        }
    }


def test_edit_description(invoke, server: JIRAServer) -> None:
    server.set_issue_response()
    server.require_method = None

    result = invoke('edit', 'GOJI-1', '--description', 'new description')

    assert result.output == 'GOJI-1 updated.\n'
    assert result.exit_code == 0

    assert server.last_request.method == 'PUT'
    assert server.last_request.body == {
        'fields': {
            'description': 'new description',
        }
    }


def test_edit_custom_field(invoke, server: JIRAServer) -> None:
    server.set_issue_response()
    server.require_method = None

    result = invoke(
        'edit',
        'GOJI-1',
        '--field',
        'customfield_1',
        'new',
        '--description',
        'new description',
    )

    assert result.output == 'GOJI-1 updated.\n'
    assert result.exit_code == 0

    assert server.last_request.method == 'PUT'
    assert server.last_request.body == {
        'fields': {
            'description': 'new description',
            'customfield_1': 'new',
        }
    }
