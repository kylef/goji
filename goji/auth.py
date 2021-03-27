import re
from netrc import netrc
from os import chmod, path
from stat import S_IRUSR, S_IWUSR
from textwrap import dedent
from typing import Optional, Tuple

from requests.compat import urlparse


def get_credentials(base_url: str) -> Tuple[Optional[str], Optional[str]]:
    hostname = urlparse(base_url).hostname
    try:
        hosts = netrc().hosts
        if hostname in hosts:
            return (hosts[hostname][0], hosts[hostname][2])
    except:
        pass

    return (None, None)


def set_credentials(base_url: str, email, password) -> None:
    hostname = urlparse(base_url).hostname
    filepath = path.expanduser('~/.netrc')
    if path.isfile(filepath):
        rcfile = open(filepath)
        contents = rcfile.read()
        rcfile.close()
        pattern = r'machine {}\n(\s+(login|password).*)+\n?'
        matcher = re.compile(pattern.format(re.escape(hostname)), re.MULTILINE)
        contents = matcher.sub('', contents)
        with open(filepath, 'w') as rcfile:
            rcfile.write(contents)
            rcfile.write(
                dedent(
                    """\n\
                    machine {}
                      login {}
                      password {}"""
                ).format(hostname, email, password)
            )

    else:
        with open(filepath, 'w') as rcfile:
            rcfile.write(
                dedent(
                    """\
                    machine {}
                      login {}
                      password {}"""
                ).format(hostname, email, password)
            )
        chmod(filepath, S_IWUSR | S_IRUSR)
