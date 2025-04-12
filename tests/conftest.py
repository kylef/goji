from typing import Iterator

import pytest
from click.testing import CliRunner

from goji.client import JIRAClient
from goji.commands import cli
from tests.server import JIRAServer


@pytest.fixture(scope='session')
def global_server() -> Iterator[JIRAServer]:
    server = JIRAServer()
    yield server
    server.shutdown()


@pytest.fixture()
def server(global_server) -> Iterator[JIRAServer]:
    yield global_server
    global_server.reset()


@pytest.fixture()
def client(server: JIRAServer) -> JIRAClient:
    return JIRAClient(server.url, ('username', 'password'))


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def invoke(server: JIRAServer, runner: CliRunner):
    def invoke(*args, **kwargs):
        args = ['--base-url', server.url] + list(args)

        if 'client' in kwargs:
            client = kwargs.pop('client')
        else:
            client = JIRAClient(server.url, ('kyle', None))

        result = runner.invoke(cli, args, obj=client, **kwargs)
        return result

    return invoke
