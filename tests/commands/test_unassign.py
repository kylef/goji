from tests.server import JIRAServer


def test_unassign(invoke, server: JIRAServer):
    server.set_assign_response('GOJI-123')

    result = invoke('unassign', 'GOJI-123')

    assert result.output == 'GOJI-123 has been unassigned.\n'
    assert result.exception is None
    assert result.exit_code is 0

    assert server.last_request.body == {'name': None}
