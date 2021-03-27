from click.testing import CliRunner

from goji.commands import cli
from tests.server import JIRAServer


def test_error_without_base_url(runner: CliRunner) -> None:
    result = runner.invoke(cli, ['open'])

    assert "Error: Missing option '--base-url'" in result.output
    assert result.exit_code != 0


def test_providing_no_credentials(invoke, server: JIRAServer) -> None:
    result = invoke('whoami', client=None)

    assert result.output == 'Error: Authentication not configured. Run `goji login`.\n'
    assert result.exit_code == 1


def test_providing_email_password(invoke, server: JIRAServer) -> None:
    server.set_user_response()

    result = invoke(
        '--email', 'kyle@example.com', '--password', 'pass', 'whoami', client=None
    )

    assert result.output == 'Kyle Fuller (kyle)\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_providing_email_no_password(invoke, server: JIRAServer) -> None:
    server.set_user_response()

    result = invoke('--email', 'kyle@example.com', 'whoami', client=None)

    assert result.output == 'Error: Email/password must be provided together.\n'
    assert result.exit_code == 1


def test_providing_password_no_email(invoke, server: JIRAServer) -> None:
    server.set_user_response()

    result = invoke('--password', 'pass', 'whoami', client=None)

    assert result.output == 'Error: Email/password must be provided together.\n'
    assert result.exit_code == 1
