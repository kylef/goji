from urlparse import urljoin
from os import system, environ
from manager import Manager
from goji.client import JIRAClient
from goji.editor import Editor


client = None
manager = Manager()


@manager.arg('issue_key')
@manager.command
def open(issue_key):
    """Open issue in a web browser"""
    url = urljoin(client.base_url, 'browse/%s' % issue_key)
    system('open %s' % url)


@manager.arg('issue_key', help='The issue identifier')
@manager.command
def show(issue_key):
    """Print issue contents"""
    issue = client.get_issue(issue_key)
    url = urljoin(client.base_url, 'browse/%s' % issue_key)

    print('\x1b[01;32m-> {issue.key}\x1b[0m'.format(issue=issue))
    print('  {issue.summary}\n'.format(issue=issue))

    if issue.description:
        for line in issue.description.splitlines():
            print('  {}'.format(line))

        print('')

    print('  - Status: {issue.status}'.format(issue=issue))
    print('  - Creator: {issue.creator}'.format(issue=issue))
    print('  - Assigned: {issue.assignee}'.format(issue=issue))
    print('  - URL: {url}'.format(url=url))

    if issue.links:
        print('\n  Related issues:')

        for link in issue.links:
            outward_issue = link.outward_issue
            print('  - %s: %s (%s)' % (link.link_type.outward.capitalize(),
                outward_issue.key, outward_issue.status))


@manager.arg('issue_key', help='The issue identifier')
@manager.arg('user', help='The assignee, or yourself if unspecified')
@manager.command
def assign(issue_key, user=None):
    """Assign an issue to a user"""
    if user is None:
        user = client.username

    if client.assign(issue_key, user):
        print('Okay, {} has been assigned to {}.'.format(issue_key, user))
    else:
        print('There was a problem assigning {} to {}.'.format(issue_key, user))


@manager.arg('issue_key', help='The issue identifier')
@manager.command
def unassign(issue_key):
    """Unassign an issue"""
    if client.assign(issue_key, None):
        print('{} has been unassigned.'.format(issue_key))
    else:
        print('There was a problem unassigning {}.'.format(issue_key))


@manager.arg('issue_key', help='The issue identifier')
@manager.command
def comment(issue_key):
    """Comment on an issue"""
    editor = Editor("""
# Leave a comment on {}
""".format(issue_key))
    comment = editor.start()

    if client.comment(issue_key, comment):
        print('Comment created')
    else:
        print('Comment failed')
        print(comment)


@manager.arg('issue_key', help='The issue identifier')
@manager.command
def edit(issue_key):
    """Edit issue description"""
    issue = client.get_issue(issue_key)
    editor = Editor(issue.description)
    description = editor.start()

    if description.strip() != issue.description.strip():
        if client.edit_issue(issue_key, {'description': description.strip()}):
            print('Okay, the description for {} has been updated.'.format(issue_key))
        else:
            print('There was an issue saving the new description:')
            print(description)


def main():
    global client

    base_url = environ.get('GOJI_JIRA_BASE_URL')

    if base_url is None:
        print('== GOJI_JIRA_BASE_URL environmental variable is not set.')
        exit()

    client = JIRAClient(base_url)

    manager.main()

