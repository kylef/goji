from datetime import datetime
from typing import Any, Dict, List, Optional


class Model(object):
    pass


class UserDetails(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> Optional['UserDetails']:
        if json:
            return cls(
                json.get('name') or '', json['displayName'], json.get('emailAddress')
            )

        return None

    def __init__(self, username: Optional[str], name: str, email: Optional[str] = None):
        self.username = username
        self.name = name
        self.email = email

    def __str__(self) -> str:
        return '{} ({})'.format(self.name, self.username or self.email)


class Issue(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Issue':
        issue = cls(json['key'])

        if 'fields' in json:
            fields = json['fields']
            issue.summary = fields.get('summary', '').rstrip()
            issue.description = fields.get('description')
            issue.creator = UserDetails.from_json(fields.get('creator'))
            if 'created' in fields:
                issue.created = datetime.fromisoformat(fields['created'].replace('+0000', '+00:00'))
            if 'resolutiondate' in fields and fields['resolutiondate']:
                issue.resolutiondate = datetime.fromisoformat(fields['resolutiondate'].replace('+0000', '+00:00'))
            issue.assignee = UserDetails.from_json(fields.get('assignee'))
            if 'status' in fields:
                issue.status = StatusDetails.from_json(fields['status'])

            resolution = fields.get('resolution', None)
            if resolution:
                issue.resolution = Resolution.from_json(resolution)
            else:
                issue.resolution = None

            issue.labels = fields.get('labels', None)

            links = []
            if 'issuelinks' in fields:
                links = [IssueLink.from_json(link) for link in fields['issuelinks']]
            issue.links = links

            issue.customfields = {}

            for (key, value) in fields.items():
                if key.startswith('customfield_'):
                    issue.customfields[key] = value

        return issue

    def __init__(self, key: str):
        self.key = key
        self.summary = None
        self.description = None
        self.creator: Optional[UserDetails] = None
        self.created: Optional[datetime] = None
        self.resolutiondate: Optional[datetime] = None
        self.assignee: Optional[UserDetails] = None
        self.status: Optional['StatusDetails'] = None
        self.resolution: Optional[Resolution] = None
        self.links: List['IssueLink'] = []
        self.labels: Optional[List[str]] = None
        self.customfields: Dict[str, Any] = {}

    def __str__(self):
        return self.key


class IssueLinkType(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'IssueLinkType':
        return cls(json['name'], json['inward'], json['outward'])

    def __init__(self, name: str, inward: str, outward: str):
        self.name = name
        self.inward = inward
        self.outward = outward


class IssueLink(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'IssueLink':
        link_type = IssueLinkType.from_json(json['type'])
        issue_link = cls(link_type)

        if 'outwardIssue' in json:
            issue_link.outward_issue = Issue.from_json(json['outwardIssue'])

        if 'inwardIssue' in json:
            issue_link.inward_issue = Issue.from_json(json['inwardIssue'])

        return issue_link

    def __init__(
        self,
        link_type: IssueLinkType,
        inward_issue: Optional[Issue] = None,
        outward_issue: Optional[Issue] = None,
    ):
        self.link_type = link_type
        self.inward_issue = inward_issue
        self.outward_issue = outward_issue

    def __str__(self) -> str:
        if self.outward_issue:
            direction = self.link_type.outward.capitalize()
            issue = self.outward_issue
        elif self.inward_issue:
            direction = self.link_type.inward.capitalize()
            issue = self.inward_issue
        else:
            raise Exception('IssueLink is missing outward or inward issue')

        return '{direction}: {issue.key} ({issue.status})'.format(
            direction=direction, issue=issue
        )


class TransitionField(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'TransitionField':
        return cls(
            id=json['fieldId'], name=json.get('name'), is_required=json.get('required')
        )

    def __init__(self, id: str, name: str, is_required: bool):
        self.id = id
        self.name = name
        self.is_required = is_required

    def __str__(self) -> str:
        return self.name


class Transition(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Transition':
        fields = list(map(TransitionField.from_json, json.get('fields', {}).values()))
        return cls(json['id'], json['name'], fields)

    def __init__(
        self, identifier: str, name: str, fields: Optional[List[TransitionField]] = None
    ):
        self.id = identifier
        self.name = name
        self.fields = fields

    def __str__(self) -> str:
        return self.name


class Comment(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Comment':
        comment = cls(json['id'], json['body'])

        if 'author' in json:
            comment.author = UserDetails.from_json(json['author'])

        return comment

    def __init__(self, identifier: str, body: str):
        self.id = identifier
        self.body = body
        self.author: Optional[UserDetails] = None

    def __str__(self) -> str:
        return self.body


class Comments(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Comments':
        return cls(
            comments=list(map(Comment.from_json, json['comments'])),
            start_at=json['startAt'],
            max_results=json['maxResults'],
            total=json['total'],
        )

    def __init__(
        self,
        comments: List[Comment],
        start_at: int,
        max_results: int,
        total: int,
    ):
        self.comments = comments
        self.start_at = start_at
        self.max_results = max_results
        self.total = total


class Sprint(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Sprint':
        return cls(json['id'], json['name'], json['state'])

    def __init__(self, identifier: str, name: str, state):
        self.id = identifier
        self.name = name
        self.state = state

    def __str__(self) -> str:
        return self.name


class StatusDetails(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'StatusDetails':
        return cls(
            json['id'],
            json['name'],
            json.get('description', None),
            StatusCategory.from_json(json['statusCategory']),
        )

    def __init__(
        self,
        identifier: str,
        name: str,
        description: Optional[str],
        status_category: 'StatusCategory',
    ):
        self.id = identifier
        self.name = name
        self.description = description
        self.status_category = status_category

    def __str__(self) -> str:
        return self.name


class Resolution(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Resolution':
        return cls(json['id'], json['name'], json.get('description', None))

    def __init__(self, identifier: str, name: str, description: Optional[str]):
        self.id = identifier
        self.name = name
        self.description = description

    def __str__(self) -> str:
        return self.name


class Attachment(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Attachment':
        return cls(
            json.get('filename'),
            int(json['size']),
            UserDetails.from_json(json['author']),
        )

    def __init__(self, filename: Optional[str], size: int, author: UserDetails):
        self.filename = filename
        self.size = size
        self.author = author


class SearchResults(Model):
    # https://docs.atlassian.com/software/jira/docs/api/REST/8.22.6/#search-search

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'SearchResults':
        return cls(
            issues=list(map(Issue.from_json, json['issues'])),
            expand=json.get('expand', '').split(','),
            start_at=json['startAt'],
            max_results=json['maxResults'],
            total=json['total'],
        )

    def __init__(
        self,
        issues: List[Issue],
        expand: List[str],
        start_at: int,
        max_results: int,
        total: int,
    ):
        self.issues = issues
        self.expand = expand
        self.start_at = start_at
        self.max_results = max_results
        self.total = total

    def __repr__(self) -> str:
        return f'<SearchResults issues={len(self.issues)} start_at={self.start_at} total={self.total}>'


"""
class IssueType(object):
    id
    description
    name

class Issue(object):
    issue type
    creator
    assignee
    url
    summary
    description
"""


class StatusCategory(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'StatusCategory':
        return cls(json['id'], json['key'], json['name'])

    def __init__(self, identifier: str, key: str, name: str):
        self.id = identifier
        self.key = key
        self.name = name

    def __str__(self) -> str:
        return self.name
