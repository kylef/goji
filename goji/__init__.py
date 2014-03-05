from urlparse import urljoin
from os import system, environ
from manager import Manager
from goji.client import JIRAClient


client = None
manager = Manager()


@manager.arg('issue_key')
@manager.command
def open(issue_key):
    url = urljoin(client.base_url, 'browse/%s' % issue_key)
    system('open %s' % url)


@manager.arg('issue_key')
@manager.command
def show(issue_key):
    issue = client.get_issue(issue_key)

    print('\x1b[01;32m-> {issue.key}\x1b[0m'.format(issue=issue))
    print('  {issue.summary}\n'.format(issue=issue))

    if issue.description:
        for line in issue.description.splitlines():
            print('  {}'.format(line))

        print('')

    print('  - Status: {issue.status}'.format(issue=issue))
    print('  - Creator: {issue.creator}'.format(issue=issue))
    print('  - Assigned: {issue.assignee}'.format(issue=issue))
    print('  - URL: https://mentallyfriendly.atlassian.net/browse/%s' % issue.key)

    if issue.links:
        print('\n  Related issues:')

        for link in issue.links:
            outward_issue = link.outward_issue
            print('  - %s: %s (%s)' % (link.link_type.outward.capitalize(),
                outward_issue.key, outward_issue.status))


def main():
    global client

    base_url = environ.get('GOJI_JIRA_BASE_URL')

    if base_url is None:
        print('== GOJI_JIRA_BASE_URL environmental variable is not set.')
        exit()

    client = JIRAClient(base_url)

    manager.main()

