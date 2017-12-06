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
        fields = json['fields']
        issue.summary = fields['summary']
        issue.description = fields.get('description')
        issue.creator = User.from_json(fields.get('creator'))
        issue.assignee = User.from_json(fields.get('assignee'))
        issue.status = fields['status']['name']

        links = []
        if 'issuelinks' in fields:
            links = [IssueLink.from_json(link) for link in fields['issuelinks']]
        issue.links = links

        return issue

    def __init__(self, key):
        self.key = key

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
        if 'outwardIssue' in json:
            return cls(link_type, Issue.from_json(json['outwardIssue']))

        return cls(link_type, Issue.from_json(json['inwardIssue']))

    def __init__(self, link_type, outward_issue):
        self.link_type = link_type
        self.outward_issue = outward_issue

    def __str__(self):
        pass


class Transition(Model):
    @classmethod
    def from_json(cls, json):
        return cls(json['id'], json['name'])

    def __init__(self, identifier, name):
        self.id = identifier
        self.name = name

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

