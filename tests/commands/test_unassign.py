from tests.commands.utils import CommandTestCase


class UnassignCommandTests(CommandTestCase):
    def test_unassign(self):
        self.server.set_assign_response('GOJI-123')

        result = self.invoke('unassign', 'GOJI-123')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'GOJI-123 has been unassigned.\n')
        self.assertEqual(result.exit_code, 0)

        self.assertEqual(self.server.last_request.body, {'name': None})
