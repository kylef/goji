from tests.server import JIRAServer


def test_create_issue_error(invoke, server: JIRAServer) -> None:
    server.set_error_response(400, "Field 'priority' is required")

    result = invoke('create', 'GOJI', 'Sprint #1', '--description', 'Desc')

    assert result.output == "Description:\n\nDesc\n\nField 'priority' is required\n"
    assert result.exit_code == 1


def test_new_title_description(invoke, server: JIRAServer) -> None:
    server.set_create_issue_response()

    result = invoke('create', 'GOJI', 'Sprint #1', '--description', 'Desc')

    assert server.last_request.body == {
        'fields': {
            'description': 'Desc',
            'project': {'key': 'GOJI'},
            'summary': 'Sprint #1',
        }
    }

    assert result.output == 'Issue GOJI-133 created\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_new_specify_component(invoke, server: JIRAServer) -> None:
    server.set_create_issue_response()

    result = invoke(
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

    assert server.last_request.body == {
        'fields': {
            'description': 'Desc',
            'project': {'key': 'GOJI'},
            'summary': 'Sprint #1',
            'components': [{'name': 'client'}, {'name': 'api'}],
        }
    }

    assert result.output == 'Issue GOJI-133 created\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_new_specify_label(invoke, server: JIRAServer) -> None:
    server.set_create_issue_response()

    result = invoke(
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

    assert server.last_request.body == {
        'fields': {
            'description': 'Desc',
            'project': {'key': 'GOJI'},
            'summary': 'Sprint #1',
            'labels': ['api', 'cli'],
        }
    }

    assert result.output == 'Issue GOJI-133 created\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_new_specify_type(invoke, server: JIRAServer) -> None:
    server.set_create_issue_response()

    result = invoke(
        'create', 'GOJI', 'Sprint #1', '--type', 'Bug', '--description', 'Desc'
    )

    assert server.last_request.body == {
        'fields': {
            'description': 'Desc',
            'issuetype': {'name': 'Bug'},
            'project': {'key': 'GOJI'},
            'summary': 'Sprint #1',
        }
    }

    assert result.output == 'Issue GOJI-133 created\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_new_specify_priority(invoke, server: JIRAServer) -> None:
    server.set_create_issue_response()

    result = invoke(
        'create', 'GOJI', 'Sprint #1', '--priority', 'hot', '--description', 'Desc'
    )

    assert server.last_request.body == {
        'fields': {
            'description': 'Desc',
            'project': {'key': 'GOJI'},
            'priority': {'name': 'hot'},
            'summary': 'Sprint #1',
        }
    }

    assert result.output == 'Issue GOJI-133 created\n'
    assert result.exception is None
    assert result.exit_code == 0
