from tests.server import JIRAServer


def test_creating_sprint(invoke, server: JIRAServer) -> None:
    server.set_create_sprint_response()

    result = invoke('sprint', 'create', '1', 'Sprint #1')

    assert result.output == 'Sprint created\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_creating_sprint_with_date(invoke, server: JIRAServer) -> None:
    server.set_create_sprint_response()

    result = invoke(
        'sprint',
        'create',
        '1',
        'Sprint #1',
        '--start',
        '10/01/18',
        '--end',
        '20/01/18',
    )

    assert result.output == 'Sprint created\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_creating_sprint_with_invalid_date(invoke, server: JIRAServer) -> None:
    server.set_create_sprint_response()

    result = invoke(
        'sprint',
        'create',
        '1',
        'Sprint #1',
        '--start',
        '10/13/18',
        '--end',
        '20/01/18',
    )

    assert result.exit_code == 2
