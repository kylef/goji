from tests.commands.utils import CommandTestCase


class CreateSprintTests(CommandTestCase):
    def test_creating_sprint(self):
        self.server.set_create_sprint_response()

        result = self.invoke('sprint', 'create', '1', 'Sprint #1')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Sprint created\n')
        self.assertEqual(result.exit_code, 0)

    def test_creating_sprint_with_date(self):
        self.server.set_create_sprint_response()

        result = self.invoke(
            'sprint',
            'create',
            '1',
            'Sprint #1',
            '--start',
            '10/01/18',
            '--end',
            '20/01/18',
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Sprint created\n')
        self.assertEqual(result.exit_code, 0)

    def test_creating_sprint_with_invalid_date(self):
        self.server.set_create_sprint_response()

        result = self.invoke(
            'sprint',
            'create',
            '1',
            'Sprint #1',
            '--start',
            '10/13/18',
            '--end',
            '20/01/18',
        )

        self.assertEqual(result.exit_code, 2)
