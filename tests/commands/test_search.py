from tests.commands.utils import CommandTestCase


class SearchCommandTests(CommandTestCase):
    def test_search(self):
        self.server.set_search_response()

        result = self.invoke('search', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'GOJI-7 My First Issue\n')
        self.assertEqual(result.exit_code, 0)

    def test_search_format_key(self):
        self.server.set_search_response()

        result = self.invoke('search', '--format', '{key}', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'GOJI-7\n')
        self.assertEqual(result.exit_code, 0)

    def test_search_format_summary(self):
        self.server.set_search_response()

        result = self.invoke('search', '--format', '{summary}', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'My First Issue\n')
        self.assertEqual(result.exit_code, 0)

    def test_search_format_description(self):
        self.server.set_search_response()

        result = self.invoke('search', '--format', '{description}', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'One\nTwo\nThree\n\n')
        self.assertEqual(result.exit_code, 0)

    def test_search_format_creator(self):
        self.server.set_search_response()

        result = self.invoke('search', '--format', '{creator}', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Kyle Fuller (kyle)\n')
        self.assertEqual(result.exit_code, 0)

    def test_search_format_assignee(self):
        self.server.set_search_response()

        result = self.invoke('search', '--format', '{assignee}', 'PROJECT=GOJI')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Delisa (delisa)\n')
        self.assertEqual(result.exit_code, 0)
