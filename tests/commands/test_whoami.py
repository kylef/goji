from tests.server import JIRAServer


def test_whoami(invoke, server: JIRAServer) -> None:
    server.set_user_response()

    result = invoke('whoami')

    assert result.output == 'Kyle Fuller (kyle)\n'
    assert result.exception is None
    assert result.exit_code == 0
