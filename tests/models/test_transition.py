import unittest

from goji.models import Transition


class TransitionTests(unittest.TestCase):
    def test_transition_creation_from_json(self) -> None:
        json = {
            'to': {
                'statusCategory': {
                    'name': 'In Progress',
                    'self': 'https://example.net/rest/api/2/statuscategory/4',
                    'id': 4,
                    'key': 'indeterminate',
                    'colorName': 'yellow',
                },
                'description': 'This issue is being actively worked on.',
                'self': 'https://example.net/rest/api/2/status/3',
                'iconUrl': 'https://example.net/icons/statuses/inprogress.png',
                'id': '3',
                'name': 'In Progress',
            },
            'hasScreen': False,
            'id': '21',
            'name': 'In Progress',
        }
        transition = Transition.from_json(json)

        assert transition.name == 'In Progress'
        assert transition.id == '21'
