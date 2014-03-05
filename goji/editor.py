from os import system, environ
from tempfile import NamedTemporaryFile
import re


class Editor(object):
    def __init__(self, prefill):
        self.prefill = prefill

    @property
    def editor(self):
        return environ.get('EDITOR', 'vi')

    def start(self):
        fd = NamedTemporaryFile()
        fd.write(self.prefill)
        fd.flush()

        system('{} {}'.format(self.editor, fd.name))

        fd.seek(0)
        data = fd.read()
        fd.close()

        regex = re.compile(r'^#.*$', re.MULTILINE)
        return regex.sub('', data)

