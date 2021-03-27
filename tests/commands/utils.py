from click.testing import CliRunner

from goji.client import JIRAClient
from goji.commands import cli
from tests.server import ServerTestCase


class CommandTestCase(ServerTestCase):
    def setUp(self) -> None:
        super(CommandTestCase, self).setUp()
        self.runner = CliRunner()

    def invoke(self, *args, **kwargs):
        args = ['--base-url', self.server.url] + list(args)

        if 'client' in kwargs:
            client = kwargs.pop('client')
        else:
            client = JIRAClient(self.server.url, ('kyle', None))

        result = self.runner.invoke(cli, args, obj=client, **kwargs)
        return result
