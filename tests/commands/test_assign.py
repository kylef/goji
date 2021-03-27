from tests.server import JIRAServer


def test_assign_specified_user(invoke, server: JIRAServer) -> None:
    server.set_assign_response('GOJI-123')

    result = invoke('assign', 'GOJI-123', 'jones')

    assert result.output == 'GOJI-123 has been assigned to jones.\n'
    assert result.exception is None
    assert result.exit_code is 0

    assert server.last_request.body == {'name': 'jones'}


def test_assign_current_user(invoke, server: JIRAServer) -> None:
    server.set_assign_response('GOJI-123')

    result = invoke('assign', 'GOJI-123')

    assert result.output == 'GOJI-123 has been assigned to kyle.\n'
    assert result.exception is None
    assert result.exit_code is 0

    assert server.last_request.body == {'name': 'kyle'}
