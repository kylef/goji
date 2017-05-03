from os import environ

import click
from requests.compat import urljoin

from goji.client import JIRAClient


@click.group()
@click.option('--base-url', envvar='GOJI_BASE_URL', required=True)
@click.pass_context
def cli(ctx, base_url):
    if not ctx.obj:
        ctx.obj = JIRAClient(base_url)


@click.argument('issue_key')
@cli.command()
@click.pass_obj
def open(client, issue_key):
    """Open issue in a web browser"""
    url = urljoin(client.base_url, 'browse/%s' % issue_key)
    click.launch(url)


@click.argument('issue_key')
@cli.command()
@click.pass_obj
def show(client, issue_key):
    """Print issue contents"""
    issue = client.get_issue(issue_key)
    url = urljoin(client.base_url, 'browse/%s' % issue_key)

    click.echo('\x1b[01;32m-> {issue.key}\x1b[0m'.format(issue=issue))
    click.echo('  {issue.summary}\n'.format(issue=issue))

    if issue.description:
        for line in issue.description.splitlines():
            click.echo('  {}'.format(line))

        click.echo('')

    click.echo('  - Status: {issue.status}'.format(issue=issue))
    click.echo('  - Creator: {issue.creator}'.format(issue=issue))
    click.echo('  - Assigned: {issue.assignee}'.format(issue=issue))
    click.echo('  - URL: {url}'.format(url=url))

    if issue.links:
        click.echo('\n  Related issues:')

        for link in issue.links:
            outward_issue = link.outward_issue
            click.echo('  - %s: %s (%s)' % (link.link_type.outward.capitalize(),
                outward_issue.key, outward_issue.status))


@click.argument('user', required=False)
@click.argument('issue_key')
@cli.command()
@click.pass_obj
def assign(client, issue_key, user):
    """Assign an issue to a user"""
    if user is None:
        user = client.username

    if client.assign(issue_key, user):
        print('Okay, {} has been assigned to {}.'.format(issue_key, user))
    else:
        print('There was a problem assigning {} to {}.'.format(issue_key, user))


@click.argument('issue_key')
@cli.command()
@click.pass_obj
def unassign(client, issue_key):
    """Unassign an issue"""
    if client.assign(issue_key, None):
        print('{} has been unassigned.'.format(issue_key))
    else:
        print('There was a problem unassigning {}.'.format(issue_key))


@click.argument('issue_key')
@cli.command()
@click.pass_obj
def comment(client, issue_key):
    """Comment on an issue"""
    MARKER = '# Leave a comment on {}'.format(issue_key)
    comment = click.edit(MARKER)

    if comment is not None and client.comment(issue_key, comment):
        print('Comment created')
    else:
        print('Comment failed')
        print(comment)


@click.argument('issue_key')
@cli.command()
@click.pass_obj
def edit(client, issue_key):
    """Edit issue description"""
    issue = client.get_issue(issue_key)
    description = click.edit(issue.description)

    if description is not None and description.strip() != issue.description.strip():
        if client.edit_issue(issue_key, {'description': description.strip()}):
            print('Okay, the description for {} has been updated.'.format(issue_key))
        else:
            print('There was an issue saving the new description:')
            print(description)


@click.argument('query')
@cli.command()
@click.pass_obj
def search(client, query):
    """Search issues using JQL"""
    issues = client.search(query)

    for issue in issues:
        print('{issue.key} {issue.summary}'.format(issue=issue))
