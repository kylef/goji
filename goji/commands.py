import click
from requests.compat import urljoin

from goji.client import JIRAClient
from goji.auth import get_credentials, set_credentials


@click.group()
@click.option('--base-url', envvar='GOJI_BASE_URL', required=True)
@click.pass_context
def cli(ctx, base_url):
    if not ctx.obj:
        if ctx.invoked_subcommand == 'login':
            ctx.obj = base_url
        else:
            ctx.obj = JIRAClient(base_url)


@click.argument('issue_key')
@cli.command('open')
@click.pass_obj
def open_command(client, issue_key):
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


@click.argument('status', required=False)
@click.argument('issue_key')
@cli.command('change-status')
@click.pass_obj
def change_status(client, issue_key, status):
    """Change the status of an issue"""
    print('Fetching possible transitions...')
    transitions = client.get_issue_transitions(issue_key)
    if len(transitions) == 0:
        print('No transitions found for {}'.format(issue_key))
        return

    if status is None:
        for index, transition in enumerate(transitions):
            print('{}: {}'.format(index, transition))
        index = click.prompt('Select a transition', type=int)
        if index < 0 or index >= len(transitions):
            print('No transitions match "{}"'.format(index))
            return
    else:
        index = -1
        for idx, transition in enumerate(transitions):
            if transition.name.lower() == status.lower():
                index = idx
        if index < 0:
            print('No transitions match "{}"'.format(status))
            return

    transition = transitions[index]
    if client.change_status(issue_key, transition.id):
        print('Okay, the status for {} is now "{}".'.format(issue_key, transition))
    else:
        print('There was an issue saving the new status as "{}"'.format(transition))


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


@cli.command()
@click.pass_obj
def login(base_url):
    """Authenticate with JIRA server"""
    email, password = get_credentials(base_url)
    if email is not None:
        if not click.confirm('This server is already configured. Override?'):
            return

    click.echo('Enter your JIRA credentials')

    email = click.prompt('Email', type=str)
    password = click.prompt('Password', type=str, hide_input=True)

    set_credentials(base_url, email, password)


@click.argument('query')
@cli.command()
@click.pass_obj
def search(client, query):
    """Search issues using JQL"""
    issues = client.search(query)

    for issue in issues:
        print('{issue.key} {issue.summary}'.format(issue=issue))
