import unittest

from goji.models import Issue, IssueLink, IssueLinkType, Status


class IssueTests(unittest.TestCase):
    def test_issue_creation_from_json(self) -> None:
        json = {
            'key': 'GOJI-1',
            'fields': {
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
                    'id': 2,
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
                                    'id': 1,
                                    'name': 'Open',
                                },
                            },
                        },
                    }
                ],
            },
        }

        issue = Issue.from_json(json)

        assert issue.key == 'GOJI-1'
        assert issue.summary == 'Issue Summary'
        assert issue.description == 'An awesome issue description'

        assert issue.creator
        assert issue.creator.username == 'kyle'

        assert issue.assignee
        assert issue.assignee.username == 'kyle'

        assert issue.status
        assert issue.status.name == 'To Do'

        assert issue.links[0].inward_issue is None
        assert issue.links[0].outward_issue
        assert issue.links[0].outward_issue.key == 'GOJI-2'
        assert issue.links[0].link_type.name == 'Relates'
        assert issue.links[0].link_type.inward == 'related to'
        assert issue.links[0].link_type.outward == 'relates to'

    def test_string_conversion(self) -> None:
        issue = Issue(key='GOJI-1')
        assert str(issue) == 'GOJI-1'


class IssueLinkTests(unittest.TestCase):
    def test_outward_issue_link_creation_from_json(self) -> None:
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
                        'id': 1,
                        'name': 'Open',
                    },
                },
            },
        }

        link = IssueLink.from_json(json)

        assert link.link_type.name == 'Relates'
        assert link.link_type.inward == 'related to'
        assert link.link_type.outward == 'relates to'

        assert link.inward_issue is None
        assert link.outward_issue
        assert link.outward_issue.key == 'GOJI-2'

    def test_inward_issue_link_creation_from_json(self) -> None:
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
                        'id': 1,
                        'name': 'Open',
                    },
                },
            },
        }

        link = IssueLink.from_json(json)

        assert link.link_type.name == 'Relates'
        assert link.link_type.inward == 'related to'
        assert link.link_type.outward == 'relates to'

        assert link.outward_issue is None
        assert link.inward_issue
        assert link.inward_issue.key == 'GOJI-2'

    def test_outward_string_conversion(self) -> None:
        link = IssueLink(IssueLinkType('relates', 'related to', 'relates to'))
        link.outward_issue = Issue('GOJI-15')
        link.outward_issue.status = Status('open', 'Open')

        assert str(link) == 'Relates to: GOJI-15 (Open)'

    def test_inward_string_conversion(self) -> None:
        link = IssueLink(IssueLinkType('relates', 'related to', 'relates to'))
        link.inward_issue = Issue('GOJI-15')
        link.inward_issue.status = Status('open', 'Open')

        assert str(link) == 'Related to: GOJI-15 (Open)'
