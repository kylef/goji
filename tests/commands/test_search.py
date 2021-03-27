from tests.server import JIRAServer


def test_search(invoke, server: JIRAServer) -> None:
    server.set_search_response()

    result = invoke('search', 'PROJECT=GOJI')

    assert result.output == 'GOJI-7 My First Issue\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_search_format_key(invoke, server: JIRAServer) -> None:
    server.set_search_response()

    result = invoke('search', '--format', '{key}', 'PROJECT=GOJI')

    assert result.output == 'GOJI-7\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_search_format_summary(invoke, server: JIRAServer) -> None:
    server.set_search_response()

    result = invoke('search', '--format', '{summary}', 'PROJECT=GOJI')

    assert result.output == 'My First Issue\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_search_format_description(invoke, server: JIRAServer) -> None:
    server.set_search_response()

    result = invoke('search', '--format', '{description}', 'PROJECT=GOJI')

    assert result.output == 'One\nTwo\nThree\n\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_search_format_creator(invoke, server: JIRAServer) -> None:
    server.set_search_response()

    result = invoke('search', '--format', '{creator}', 'PROJECT=GOJI')

    assert result.output == 'Kyle Fuller (kyle)\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_search_format_assignee(invoke, server: JIRAServer) -> None:
    server.set_search_response()

    result = invoke('search', '--format', '{assignee}', 'PROJECT=GOJI')

    assert result.output == 'Delisa (delisa)\n'
    assert result.exception is None
    assert result.exit_code == 0
