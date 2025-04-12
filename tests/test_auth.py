import os
from stat import S_IRUSR, S_IWUSR
from textwrap import dedent

from click.testing import CliRunner

from goji.auth import get_credentials, set_credentials


def test_empty_get_credentials(tmp_path):
    base_url = 'https://goji.example.com/'
    os.environ['HOME'] = str(tmp_path)
    login, password = get_credentials(base_url)
    assert login is None
    assert password is None


def test_preset_get_credentials(tmp_path):
    base_url = 'https://goji.example.com/'
    os.environ['HOME'] = str(tmp_path)
    netrc_path = tmp_path / '.netrc'
    netrc_path.write_text(
        dedent(
            """\
            machine goji.example.com
              login delisa
              password foober_1-"""
        )
    )
    netrc_path.chmod(S_IWUSR | S_IRUSR)
    login, password = get_credentials(base_url)
    assert login == 'delisa'
    assert password == 'foober_1-'


def test_new_set_credentials(tmp_path):
    base_url = 'https://goji.example.com/'
    os.environ['HOME'] = str(tmp_path)
    netrc_path = tmp_path / '.netrc'
    netrc_path.write_text(
        dedent(
            """\
            machine goji2.example.com
              login delisa
              password foober_1-"""
        )
    )
    netrc_path.chmod(S_IWUSR | S_IRUSR)
    set_credentials(base_url, 'kylef', '39481-a')
    assert netrc_path.read_text() == dedent(
        """\
        machine goji2.example.com
          login delisa
          password foober_1-
        machine goji.example.com
          login kylef
          password 39481-a"""
    )


def test_override_set_credentials(tmp_path):
    base_url = 'https://goji.example.com/'
    os.environ['HOME'] = str(tmp_path)
    netrc_path = tmp_path / '.netrc'
    netrc_path.write_text(
        dedent(
            """\
            machine goji3.example.com
              login df
              password mypassword
            machine goji.example.com
              login delisa
              password foobar+1
            machine goji2.example.com
              login delisa
              password foober_1-"""
        )
    )
    netrc_path.chmod(S_IWUSR | S_IRUSR)
    set_credentials(base_url, 'kylef', '39481-a')
    assert netrc_path.read_text() == dedent(
        """\
        machine goji3.example.com
          login df
          password mypassword
        machine goji2.example.com
          login delisa
          password foober_1-
        machine goji.example.com
          login kylef
          password 39481-a"""
    )


def test_create_file_set_credentials(tmp_path):
    base_url = 'https://goji.example.com/'
    os.environ['HOME'] = str(tmp_path)
    netrc_path = tmp_path / '.netrc'
    set_credentials(base_url, 'kylef', '39481-a')
    assert netrc_path.read_text() == dedent(
        """\
        machine goji.example.com
          login kylef
          password 39481-a"""
    )
