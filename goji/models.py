from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class UserDetails:
    username: Optional[str]
    name: str
    email: Optional[str] = None

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> Optional['UserDetails']:
        if json:
            return cls(
                json.get('name') or '', json['displayName'], json.get('emailAddress')
            )

        return None

    def __str__(self) -> str:
        return '{} ({})'.format(self.name, self.username or self.email)


@dataclass
class Issue:
    key: str
    summary: Optional[str] = None
    description: Optional[str] = None
    creator: Optional[UserDetails] = None
    created: Optional[datetime] = None
    resolutiondate: Optional[datetime] = None
    assignee: Optional[UserDetails] = None
    status: Optional['StatusDetails'] = None
    resolution: Optional['Resolution'] = None
    links: List['IssueLink'] = field(default_factory=list)
    labels: Optional[List[str]] = None
    customfields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Issue':
        issue = cls(json['key'])

        if 'fields' in json:
            fields = json['fields']
            issue.summary = fields.get('summary', '').rstrip()
            issue.description = fields.get('description')
            issue.creator = UserDetails.from_json(fields.get('creator'))
            if 'created' in fields:
                issue.created = datetime.fromisoformat(
                    fields['created'].replace('+0000', '+00:00')
                )
            if 'resolutiondate' in fields and fields['resolutiondate']:
                issue.resolutiondate = datetime.fromisoformat(
                    fields['resolutiondate'].replace('+0000', '+00:00')
                )
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

            for key, value in fields.items():
                if key.startswith('customfield_'):
                    issue.customfields[key] = value

        return issue

    def __str__(self):
        return self.key


@dataclass
class IssueLinkType:
    name: str
    inward: str
    outward: str

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'IssueLinkType':
        return cls(json['name'], json['inward'], json['outward'])


@dataclass
class IssueLink:
    link_type: IssueLinkType
    inward_issue: Optional[Issue] = None
    outward_issue: Optional[Issue] = None

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'IssueLink':
        link_type = IssueLinkType.from_json(json['type'])
        issue_link = cls(link_type)

        if 'outwardIssue' in json:
            issue_link.outward_issue = Issue.from_json(json['outwardIssue'])

        if 'inwardIssue' in json:
            issue_link.inward_issue = Issue.from_json(json['inwardIssue'])

        return issue_link

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


@dataclass
class TransitionField:
    id: str
    name: str
    is_required: bool

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'TransitionField':
        return cls(
            id=json['fieldId'], name=json.get('name'), is_required=json.get('required')
        )

    def __str__(self) -> str:
        return self.name


@dataclass
class Transition:
    id: str
    name: str
    fields: Optional[List[TransitionField]]

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Transition':
        fields = list(map(TransitionField.from_json, json.get('fields', {}).values()))
        return cls(json['id'], json['name'], fields)

    def __str__(self) -> str:
        return self.name


@dataclass
class Comment:
    id: str
    body: str
    author: Optional[UserDetails] = None

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Comment':
        comment = cls(json['id'], json['body'])

        if 'author' in json:
            comment.author = UserDetails.from_json(json['author'])

        return comment

    def __str__(self) -> str:
        return self.body


@dataclass
class Comments:
    comments: List[Comment]
    start_at: int
    max_results: int
    total: int

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Comments':
        return cls(
            comments=list(map(Comment.from_json, json['comments'])),
            start_at=json['startAt'],
            max_results=json['maxResults'],
            total=json['total'],
        )


@dataclass
class Sprint:
    identifier: str
    name: str
    state: Any

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Sprint':
        return cls(json['id'], json['name'], json['state'])

    def __str__(self) -> str:
        return self.name


@dataclass
class StatusDetails:
    identifier: str
    name: str
    description: Optional[str]
    status_category: 'StatusCategory'

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'StatusDetails':
        return cls(
            json['id'],
            json['name'],
            json.get('description', None),
            StatusCategory.from_json(json['statusCategory']),
        )

    def __str__(self) -> str:
        return self.name


@dataclass
class Resolution:
    identifier: str
    name: str
    description: Optional[str]

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Resolution':
        return cls(json['id'], json['name'], json.get('description', None))

    def __str__(self) -> str:
        return self.name


@dataclass
class Attachment:
    filename: Optional[str]
    size: int
    author: UserDetails

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'Attachment':
        return cls(
            json.get('filename'),
            int(json['size']),
            UserDetails.from_json(json['author']),
        )


@dataclass
class SearchResults:
    # https://docs.atlassian.com/software/jira/docs/api/REST/8.22.6/#search-search

    issues: List[Issue]
    expand: List[str]
    start_at: int
    max_results: int
    total: int

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'SearchResults':
        return cls(
            issues=list(map(Issue.from_json, json['issues'])),
            expand=json.get('expand', '').split(','),
            start_at=json['startAt'],
            max_results=json['maxResults'],
            total=json['total'],
        )

    def __repr__(self) -> str:
        return f'<SearchResults issues={len(self.issues)} start_at={self.start_at} total={self.total}>'


@dataclass
class StatusCategory:
    id: str
    key: str
    name: str

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> 'StatusCategory':
        return cls(json['id'], json['key'], json['name'])

    def __str__(self) -> str:
        return self.name
