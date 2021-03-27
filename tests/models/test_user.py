import unittest

from goji.models import User


class UserTests(unittest.TestCase):
    def test_user_creation_from_json(self) -> None:
        json = {
            'name': 'kyle',
            'emailAddress': 'kyle@example.com',
            'displayName': 'Kyle Fuller',
        }

        user = User.from_json(json)

        assert user
        assert user.username == 'kyle'
        assert user.name == 'Kyle Fuller'
        assert user.email == 'kyle@example.com'

    def test_string_conversion(self) -> None:
        user = User(username='kyle', name='Kyle Fuller')
        assert str(user) == 'Kyle Fuller (kyle)'
