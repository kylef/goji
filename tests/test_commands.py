from click.testing import CliRunner

from goji.commands import cli
from tests.commands.utils import CommandTestCase


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
