import unittest
import os
from stat import S_IRUSR, S_IWUSR
from textwrap import dedent

from click.testing import CliRunner

from goji.auth import get_credentials, set_credentials


class AuthTests(unittest.TestCase):
    def test_empty_get_credentials(self):
        base_url = 'https://goji.example.com/'
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.environ['HOME'] = './'
            login, password = get_credentials(base_url)
            self.assertIsNone(login)
            self.assertIsNone(password)

    def test_preset_get_credentials(self):
        base_url = 'https://goji.example.com/'
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.environ['HOME'] = './'
            with open('.netrc', 'w') as rcfile:
                rcfile.write(dedent("""\
                        machine goji.example.com
                          login delisa
                          password foober_1-"""))
            os.chmod('.netrc', S_IWUSR | S_IRUSR)
            login, password = get_credentials(base_url)
            self.assertEqual(login, 'delisa')
            self.assertEqual(password, 'foober_1-')

    def test_new_set_credentials(self):
        base_url = 'https://goji.example.com/'
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.environ['HOME'] = './'
            with open('.netrc', 'w') as rcfile:
                rcfile.write(dedent("""\
                        machine goji2.example.com
                          login delisa
                          password foober_1-"""))
            os.chmod('.netrc', S_IWUSR | S_IRUSR)
            set_credentials(base_url, 'kylef', '39481-a')
            with open('.netrc', 'r') as rcfile:
                self.assertEqual(dedent("""\
                        machine goji2.example.com
                          login delisa
                          password foober_1-
                        machine goji.example.com
                          login kylef
                          password 39481-a"""), rcfile.read())

    def test_override_set_credentials(self):
        base_url = 'https://goji.example.com/'
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.environ['HOME'] = './'
            with open('.netrc', 'w') as rcfile:
                rcfile.write(dedent("""\
                        machine goji3.example.com
                          login df
                          password mypassword
                        machine goji.example.com
                          login delisa
                          password foobar+1
                        machine goji2.example.com
                          login delisa
                          password foober_1-"""))
            os.chmod('.netrc', S_IWUSR | S_IRUSR)
            set_credentials(base_url, 'kylef', '39481-a')
            with open('.netrc', 'r') as rcfile:
                self.assertEqual(dedent("""\
                        machine goji3.example.com
                          login df
                          password mypassword
                        machine goji2.example.com
                          login delisa
                          password foober_1-
                        machine goji.example.com
                          login kylef
                          password 39481-a"""), rcfile.read())

    def test_create_file_set_credentials(self):
        base_url = 'https://goji.example.com/'
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.environ['HOME'] = './'
            set_credentials(base_url, 'kylef', '39481-a')
            with open('.netrc', 'r') as rcfile:
                self.assertEqual(dedent("""\
                        machine goji.example.com
                          login kylef
                          password 39481-a"""), rcfile.read())
