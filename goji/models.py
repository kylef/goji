from typing import Any, Dict, List, Optional


class Model(object):
    pass


class User(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> Optional['User']:
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
            issue.summary = fields['summary'].rstrip()
            issue.description = fields.get('description')
            issue.creator = User.from_json(fields.get('creator'))
            issue.assignee = User.from_json(fields.get('assignee'))
            issue.status = Status.from_json(fields['status'])

            resolution = fields.get('resolution', None)
            if resolution:
                issue.resolution = Resolution.from_json(resolution)
            else:
                issue.resolution = None

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
        self.creator: Optional[User] = None
        self.assignee: Optional[User] = None
        self.status: Optional['Status'] = None
        self.resolution: Optional[Resolution] = None
        self.links: List['IssueLink'] = []
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


class Transition(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Transition':
        return cls(json['id'], json['name'])

    def __init__(self, identifier: str, name: str):
        self.id = identifier
        self.name = name

    def __str__(self) -> str:
        return self.name


class Comment(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Comment':
        comment = cls(json['id'], json['body'])

        if 'author' in json:
            comment.author = User.from_json(json['author'])

        return comment

    def __init__(self, identifier: str, message: str):
        self.id = identifier
        self.message = message
        self.author: Optional[User] = None

    def __str__(self) -> str:
        return self.message


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


class Status(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Status':
        return cls(json['id'], json['name'], json.get('description', None))

    def __init__(self, identifier: str, name: str, description: Optional[str] = None):
        self.id = identifier
        self.name = name
        self.description = description

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
        return cls(json.get('filename'), int(json['size']))

    def __init__(self, filename: Optional[str], size: int):
        self.filename = filename
        self.size = size


class SearchResults(Model):
    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'SearchResults':
        return cls(issues=list(map(Issue.from_json, json['issues'])))

    def __init__(self, issues: List[Issue]):
        self.issues = issues


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
