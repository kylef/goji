from tests.commands.utils import CommandTestCase


class WhoamiCommandTests(CommandTestCase):
    def test_whoami(self):
        self.server.set_user_response()

        result = self.invoke('whoami')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Kyle Fuller (kyle)\n')
        self.assertEqual(result.exit_code, 0)
