import unittest

from goji.models import User


class UserTests(unittest.TestCase):
    def test_user_creation_from_json(self):
        json = {
            'name': 'kyle',
            'emailAddress': 'inbox@kylefuller.co.uk',
            'displayName': 'Kyle Fuller',
        }

        user = User.from_json(json)

        self.assertEqual(user.username, 'kyle')
        self.assertEqual(user.name, 'Kyle Fuller')
        self.assertEqual(user.email, 'inbox@kylefuller.co.uk')

    def test_string_conversion(self):
        user = User(username='kyle', name='Kyle Fuller')
        self.assertEqual(str(user), 'Kyle Fuller (kyle)')
