import os

from tests.commands.utils import CommandTestCase


class LoginCommandTests(CommandTestCase):
    def test_login(self):
        self.server.set_user_response()

        with self.runner.isolated_filesystem():
            result = self.invoke('login', client=None, input='email\npassword\n')

            with open(os.path.expanduser('~/.netrc')) as fp:
                self.assertEqual(
                    fp.read(), 'machine 127.0.0.1\n  login email\n  password password'
                )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            self.server.last_request.headers['Authorization'],
            'Basic ZW1haWw6cGFzc3dvcmQ=',
        )

    def test_login_incorret_credentials(self):
        self.server.set_error_response(401, 'Authorization')
        self.server.response.headers['Content-Type'] = 'text/plain'

        result = self.invoke('login', client=None, input='email\npassword\n')

        self.assertTrue(
            'Error: Incorrect credentials. Try `goji login`.' in result.output
        )
        self.assertEqual(result.exit_code, 1)
