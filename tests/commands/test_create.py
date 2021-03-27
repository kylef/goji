from tests.commands.utils import CommandTestCase


class NewCommandTests(CommandTestCase):
    def test_create_issue_error(self):
        self.server.set_error_response(400, "Field 'priority' is required")

        result = self.invoke('create', 'GOJI', 'Sprint #1', '--description', 'Desc')

        self.assertEqual(
            result.output, "Description:\n\nDesc\n\nField 'priority' is required\n"
        )
        self.assertEqual(result.exit_code, 1)

    def test_new_title_description(self):
        self.server.set_create_issue_response()

        result = self.invoke('create', 'GOJI', 'Sprint #1', '--description', 'Desc')

        self.assertEqual(
            self.server.last_request.body,
            {
                'fields': {
                    'description': 'Desc',
                    'project': {'key': 'GOJI'},
                    'summary': 'Sprint #1',
                }
            },
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Issue GOJI-133 created\n')
        self.assertEqual(result.exit_code, 0)

    def test_new_specify_component(self):
        self.server.set_create_issue_response()

        result = self.invoke(
            'create',
            'GOJI',
            'Sprint #1',
            '--component',
            'client',
            '-c',
            'api',
            '--description',
            'Desc',
        )

        self.assertEqual(
            self.server.last_request.body,
            {
                'fields': {
                    'description': 'Desc',
                    'project': {'key': 'GOJI'},
                    'summary': 'Sprint #1',
                    'components': [{'name': 'client'}, {'name': 'api'}],
                }
            },
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Issue GOJI-133 created\n')
        self.assertEqual(result.exit_code, 0)

    def test_new_specify_label(self):
        self.server.set_create_issue_response()

        result = self.invoke(
            'create',
            'GOJI',
            'Sprint #1',
            '--label',
            'api',
            '--label',
            'cli',
            '--description',
            'Desc',
        )

        self.assertEqual(
            self.server.last_request.body,
            {
                'fields': {
                    'description': 'Desc',
                    'project': {'key': 'GOJI'},
                    'summary': 'Sprint #1',
                    'labels': ['api', 'cli'],
                }
            },
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Issue GOJI-133 created\n')
        self.assertEqual(result.exit_code, 0)

    def test_new_specify_type(self):
        self.server.set_create_issue_response()

        result = self.invoke(
            'create', 'GOJI', 'Sprint #1', '--type', 'Bug', '--description', 'Desc'
        )

        self.assertEqual(
            self.server.last_request.body,
            {
                'fields': {
                    'description': 'Desc',
                    'issuetype': {'name': 'Bug'},
                    'project': {'key': 'GOJI'},
                    'summary': 'Sprint #1',
                }
            },
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Issue GOJI-133 created\n')
        self.assertEqual(result.exit_code, 0)

    def test_new_specify_priority(self):
        self.server.set_create_issue_response()

        result = self.invoke(
            'create', 'GOJI', 'Sprint #1', '--priority', 'hot', '--description', 'Desc'
        )

        self.assertEqual(
            self.server.last_request.body,
            {
                'fields': {
                    'description': 'Desc',
                    'project': {'key': 'GOJI'},
                    'priority': {'name': 'hot'},
                    'summary': 'Sprint #1',
                }
            },
        )

        self.assertIsNone(result.exception)
        self.assertEqual(result.output, 'Issue GOJI-133 created\n')
        self.assertEqual(result.exit_code, 0)
