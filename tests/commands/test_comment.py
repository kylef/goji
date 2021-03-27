from tests.commands.utils import CommandTestCase


class CommentCommandTests(CommandTestCase):
    def test_commenting_with_message(self):
        self.server.set_comment_response('GOJI-311')

        result = self.invoke('comment', 'GOJI-311', '-m', 'My short one-line comment')

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Comment created\n')
        self.assertEqual(result.exit_code, 0)

    def test_commenting_producing_error(self):
        self.server.set_error_response(404, 'Issue Does Not Exist')

        result = self.invoke('comment', 'GOJI-311', '-m', 'My short one-line comment')

        self.assertEqual(
            result.output,
            'Comment:\n\nMy short one-line comment\n\nIssue Does Not Exist\n',
        )
        self.assertEqual(result.exit_code, 1)
