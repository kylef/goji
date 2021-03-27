from tests.server import JIRAServer


def test_commenting_with_message(invoke, server: JIRAServer) -> None:
    server.set_comment_response('GOJI-311')

    result = invoke('comment', 'GOJI-311', '-m', 'My short one-line comment')

    assert result.output == 'Comment created\n'
    assert result.exception is None
    assert result.exit_code == 0


def test_commenting_producing_error(invoke, server: JIRAServer) -> None:
    server.set_error_response(404, 'Issue Does Not Exist')

    result = invoke('comment', 'GOJI-311', '-m', 'My short one-line comment')

    assert (
        result.output
        == 'Comment:\n\nMy short one-line comment\n\nIssue Does Not Exist\n'
    )
    assert result.exit_code == 1
