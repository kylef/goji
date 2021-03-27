import os

from tests.server import JIRAServer


def test_login(runner, invoke, server: JIRAServer) -> None:
    server.set_user_response()

    with runner.isolated_filesystem():
        result = invoke('login', client=None, input='email\npassword\n')

        with open(os.path.expanduser('~/.netrc')) as fp:
            assert fp.read() == 'machine 127.0.0.1\n  login email\n  password password'

    assert result.exception is None
    assert result.exit_code == 0
    assert server.last_request.headers['Authorization'] == 'Basic ZW1haWw6cGFzc3dvcmQ='


def test_login_with_incorret_credentials(invoke, server: JIRAServer) -> None:
    server.set_error_response(401, 'Authorization')
    server.response.headers['Content-Type'] = 'text/plain'

    result = invoke('login', client=None, input='email\npassword\n')

    assert 'Error: Incorrect credentials. Try `goji login`.' in result.output
    assert result.exit_code == 1
