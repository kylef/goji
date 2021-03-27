from tests.commands.utils import CommandTestCase


class ShowCommandTests(CommandTestCase):
    def test_show__without_issue_key(self) -> None:
        result = self.invoke('show')

        assert "Error: Missing argument 'ISSUE_KEY'" in result.output
        self.assertNotEqual(result.exit_code, 0)

    def test_show_with_issue_key(self):
        self.server.set_issue_response()

        result = self.invoke('show', 'GOJI-1')
        output = result.output.replace(self.server.url, 'https://example.com')

        expected = '''-> GOJI-1
  Example Issue

  Issue Description

  - Status: Open
  - Creator: Kyle Fuller (kyle)
  - Assigned: Delisa (delisa)
  - URL: https://example.com/browse/GOJI-1
'''

        assert output == expected
        assert result.exit_code == 0


