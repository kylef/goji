from tests.commands.utils import CommandTestCase


class AssignCommandTests(CommandTestCase):
    def test_assign_specified_user(self):
        self.server.set_assign_response('GOJI-123')

        result = self.invoke('assign', 'GOJI-123', 'jones')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'GOJI-123 has been assigned to jones.\n')
        self.assertEqual(result.exit_code, 0)

        self.assertEqual(self.server.last_request.body, {'name': 'jones'})

    def test_assign_current_user(self):
        self.server.set_assign_response('GOJI-123')

        result = self.invoke('assign', 'GOJI-123')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'GOJI-123 has been assigned to kyle.\n')
        self.assertEqual(result.exit_code, 0)

        self.assertEqual(self.server.last_request.body, {'name': 'kyle'})
