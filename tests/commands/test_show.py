from tests.server import JIRAServer


def test_show_without_issue(invoke) -> None:
    result = invoke('show')

    assert "Error: Missing argument 'ISSUE_KEY'" in result.output
    assert result.exit_code != 0


def test_show(invoke, server: JIRAServer) -> None:
    server.set_issue_response()

    result = invoke('show', 'GOJI-1')
    output = result.output.replace(server.url, 'https://example.com')

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
