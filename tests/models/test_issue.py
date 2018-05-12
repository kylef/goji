import unittest
from goji.models import Issue, IssueLink, IssueLinkType


class IssueTests(unittest.TestCase):
    def test_issue_creation_from_json(self):
        json = {
            'key': 'GOJI-1',
            'fields': {
                'status': {
                    'name': 'closed'
                },
                'summary': 'Issue Summary',
                'description': 'An awesome issue description',
                'creator': {
                    'name': 'kyle',
                    'displayName': 'Kyle Fuller',
                },
                'assignee': {
                    'name': 'kyle',
                    'displayName': 'Kyle Fuller',
                },
                'status': {
                    'name': 'To Do',
                },
                'issuelinks': [
                    {
                        'type': {
                            'name': 'Relates',
                            'inward': 'related to',
                            'outward': 'relates to',
                        },
                        'outwardIssue': {
                            'key': 'GOJI-2',
                            'fields': {
                                'summary': 'Hello world',
                                'status': {
                                    'name': 'Open',
                                },
                            }
                        }
                    }
                ]
            },
        }

        issue = Issue.from_json(json)

        self.assertEqual(issue.key, 'GOJI-1')
        self.assertEqual(issue.summary, 'Issue Summary')
        self.assertEqual(issue.description, 'An awesome issue description')
        self.assertEqual(issue.creator.username, 'kyle')
        self.assertEqual(issue.assignee.username, 'kyle')
        self.assertEqual(issue.status, 'To Do')
        self.assertEqual(issue.links[0].outward_issue.key, 'GOJI-2')
        self.assertEqual(issue.links[0].link_type.name, 'Relates')
        self.assertEqual(issue.links[0].link_type.inward, 'related to')
        self.assertEqual(issue.links[0].link_type.outward, 'relates to')

    def test_string_conversion(self):
        issue = Issue(key='GOJI-1')
        self.assertEqual(str(issue), 'GOJI-1')


class IssueLinkTests(unittest.TestCase):
    def test_outward_issue_link_creation_from_json(self):
        json = {
            'type': {
                'name': 'Relates',
                'inward': 'related to',
                'outward': 'relates to',
            },
            'outwardIssue': {
                'key': 'GOJI-2',
                'fields': {
                    'summary': 'Hello world',
                    'status': {
                        'name': 'Open',
                    },
                }
            }
        }

        link = IssueLink.from_json(json)

        self.assertEqual(link.link_type.name, 'Relates')
        self.assertEqual(link.link_type.inward, 'related to')
        self.assertEqual(link.link_type.outward, 'relates to')
        self.assertIsNone(link.inward_issue)
        self.assertEqual(link.outward_issue.key, 'GOJI-2')

    def test_inward_issue_link_creation_from_json(self):
        json = {
            'type': {
                'name': 'Relates',
                'inward': 'related to',
                'outward': 'relates to',
            },
            'inwardIssue': {
                'key': 'GOJI-2',
                'fields': {
                    'summary': 'Hello world',
                    'status': {
                        'name': 'Open',
                    },
                }
            }
        }

        link = IssueLink.from_json(json)

        self.assertEqual(link.link_type.name, 'Relates')
        self.assertEqual(link.link_type.inward, 'related to')
        self.assertEqual(link.link_type.outward, 'relates to')
        self.assertIsNone(link.outward_issue)
        self.assertEqual(link.inward_issue.key, 'GOJI-2')

    def test_outward_string_conversion(self):
        link = IssueLink(IssueLinkType('relates', 'related to', 'relates to'))
        link.outward_issue = Issue('GOJI-15')
        link.outward_issue.status = 'Open'

        self.assertEqual(str(link), 'Relates to: GOJI-15 (Open)')

    def test_inward_string_conversion(self):
        link = IssueLink(IssueLinkType('relates', 'related to', 'relates to'))
        link.inward_issue = Issue('GOJI-15')
        link.inward_issue.status = 'Open'

        self.assertEqual(str(link), 'Related to: GOJI-15 (Open)')
