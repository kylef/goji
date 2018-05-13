class Model(object):
    pass


class User(Model):
    @classmethod
    def from_json(cls, json):
        if json:
            return cls(json['name'], json['displayName'], json.get('emailAddress'))

    def __init__(self, username, name, email=None):
        self.username = username
        self.name = name
        self.email = email

    def __str__(self):
        return '{} ({})'.format(self.name, self.username)


class Issue(Model):
    @classmethod
    def from_json(cls, json):
        issue = cls(json['key'])

        if 'fields' in json:
            fields = json['fields']
            issue.summary = fields['summary']
            issue.description = fields.get('description')
            issue.creator = User.from_json(fields.get('creator'))
            issue.assignee = User.from_json(fields.get('assignee'))
            issue.status = Status.from_json(fields['status'])

            links = []
            if 'issuelinks' in fields:
                links = [IssueLink.from_json(link) for link in fields['issuelinks']]
            issue.links = links

        return issue

    def __init__(self, key):
        self.key = key
        self.summary = None
        self.description = None
        self.creator = None
        self.assignee = None
        self.status = None

    def __str__(self):
        return self.key


class IssueLinkType(Model):
    @classmethod
    def from_json(cls, json):
        return cls(json['name'], json['inward'], json['outward'])

    def __init__(self, name, inward, outward):
        self.name = name
        self.inward = inward
        self.outward = outward


class IssueLink(Model):
    @classmethod
    def from_json(cls, json):
        link_type = IssueLinkType.from_json(json['type'])
        issue_link = cls(link_type)

        if 'outwardIssue' in json:
            issue_link.outward_issue = Issue.from_json(json['outwardIssue'])

        if 'inwardIssue' in json:
            issue_link.inward_issue = Issue.from_json(json['inwardIssue'])

        return issue_link

    def __init__(self, link_type, inward_issue=None, outward_issue=None):
        self.link_type = link_type
        self.inward_issue = inward_issue
        self.outward_issue = outward_issue

    def __str__(self):
        if self.outward_issue:
            direction = self.link_type.outward.capitalize()
            issue = self.outward_issue
        elif self.inward_issue:
            direction = self.link_type.inward.capitalize()
            issue = self.inward_issue

        return '{direction}: {issue.key} ({issue.status})'.format(direction=direction, issue=issue)


class Transition(Model):
    @classmethod
    def from_json(cls, json):
        return cls(json['id'], json['name'])

    def __init__(self, identifier, name):
        self.id = identifier
        self.name = name

    def __str__(self):
        return self.name


class Comment(Model):
    @classmethod
    def from_json(cls, json):
        comment = cls(json['id'], json['body'])

        if 'author' in json:
            comment.author = User.from_json(json['author'])

        return comment

    def __init__(self, identifier, message):
        self.id = identifier
        self.message = message
        self.author = None

    def __str__(self):
        return self.message


class Sprint(Model):
    @classmethod
    def from_json(cls, json):
        return cls(json['id'], json['name'], json['state'])

    def __init__(self, identifier, name, state):
        self.id = identifier
        self.name = name
        self.state = state

    def __str__(self):
        return self.name


class Status(Model):
    @classmethod
    def from_json(cls, json):
        return cls(json['id'], json['name'], json.get('description', None))

    def __init__(self, identifier, name, description):
        self.id = identifier
        self.name = name
        self.description = description

    def __str__(self):
        return self.name


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
