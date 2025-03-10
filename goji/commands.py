from functools import partial
import importlib
import io
import pkgutil
import sys
from os import isatty
from string import Formatter
from typing import Optional

import click
from requests.compat import urljoin

from goji.auth import get_credentials, set_credentials
from goji.client import JIRAClient
from goji.config import Configuration
from goji.utils import Datetime


def check_login(client) -> None:
    response = client.get('myself', allow_redirects=False)

    if response.status_code == 401:
        raise click.ClickException('Incorrect credentials. Try `goji login`.')


@click.group()
@click.option('--profile', envvar='GOJI_PROFILE', default='default')
@click.option('--base-url', envvar='GOJI_BASE_URL')
@click.option('--email', envvar='GOJI_EMAIL', default=None)
@click.option('--password', envvar='GOJI_PASSWORD', default=None)
@click.pass_context
def cli(
    ctx, profile: str, base_url: str, email: Optional[str], password: Optional[str]
) -> None:
    config = Configuration.load()
    p = config.profiles.get(profile.lower())

    if p:
        if not base_url:
            base_url = p.url

        if p.email and not email:
            email = p.email

    if not p and profile != 'default':
        raise click.ClickException(f'Profile {profile} not found')

    if not base_url:
        raise click.ClickException('JIRA base URL is not configured')

    if not ctx.obj:
        if ctx.invoked_subcommand == 'login':
            ctx.obj = base_url
        elif email and password:
            ctx.obj = JIRAClient(base_url, auth=(email, password))
        elif email and not password:
            raise click.ClickException('Password is not configured.')
        elif not email and password:
            raise click.ClickException('Email is not configured.')
        else:
            email, password = get_credentials(base_url)

            if not email or not password:
                raise click.ClickException(
                    'Authentication not configured. Run `goji login`.'
                )

            ctx.obj = JIRAClient(base_url, auth=(email, password))


@cli.command('whoami')
@click.pass_obj
def whoami(client: JIRAClient) -> None:
    """View information regarding current user"""
    user = client.get_user()
    click.echo(user)


@click.argument('issue_key')
@cli.command('open')
@click.pass_obj
def open_command(client: JIRAClient, issue_key: str) -> None:
    """Open issue in a web browser"""
    url = urljoin(client.base_url, 'browse/%s' % issue_key)
    click.launch(url)


@click.argument('issue_key')
@cli.command()
@click.pass_obj
def show(client: JIRAClient, issue_key: str) -> None:
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
            click.echo('    - {}'.format(link))


@click.argument('user', required=False)
@click.argument('issue_key')
@cli.command()
@click.pass_obj
def assign(client: JIRAClient, issue_key: str, user: Optional[str]) -> None:
    """Assign an issue to a user"""

    if user is None:
        user = client.username

    client.assign(issue_key, user)
    click.echo('{} has been assigned to {}.'.format(issue_key, user))


@click.argument('issue_key')
@cli.command()
@click.pass_obj
def unassign(client: JIRAClient, issue_key: str) -> None:
    """Unassign an issue"""

    client.assign(issue_key, None)
    click.echo('{} has been unassigned.'.format(issue_key))


@click.argument('status', required=False)
@click.argument('issue_key')
@cli.command('change-status')
@click.pass_obj
def change_status(client: JIRAClient, issue_key: str, status: Optional[str]) -> None:
    """Change the status of an issue"""
    click.echo('Fetching possible transitions...')
    transitions = client.get_issue_transitions(issue_key)
    if len(transitions) == 0:
        click.echo('No transitions found for {}'.format(issue_key))
        return

    if status is None:
        for index, transition in enumerate(transitions):
            click.echo('{}: {}'.format(index, transition))
        index = click.prompt('Select a transition', type=int)
        if index < 0 or index >= len(transitions):
            click.echo('No transitions match "{}"'.format(index))
            return
    else:
        index = -1
        for idx, transition in enumerate(transitions):
            if transition.name.lower() == status.lower():
                index = idx
        if index < 0:
            click.echo('No transitions match "{}"'.format(status))
            return

    transition = transitions[index]
    client.change_status(issue_key, transition.id)
    click.echo('Okay, the status for {} is now "{}".'.format(issue_key, transition))


@click.argument('issue_key')
@cli.command()
@click.pass_obj
def comments(client: JIRAClient, issue_key: str) -> None:
    comments = client.comments(issue_key)

    for index, comment in enumerate(comments.comments):
        if index != 0:
            print()

        print('=' * 60)
        print(comment.author)
        print(comment)


@click.option('--message', '-m', help='Message to comment.')
@click.argument('issue_key')
@cli.command()
@click.pass_obj
def comment(client: JIRAClient, message: Optional[str], issue_key: str) -> None:
    """Comment on an issue"""

    if not message:
        MARKER = '# Leave a comment on {}'.format(issue_key)
        message = click.edit(MARKER)

    if message is None or len(message) == 0:
        return

    try:
        client.comment(issue_key, message)
        click.echo('Comment created')
    except Exception as e:
        click.echo('Comment:\n')
        click.echo(message)
        click.echo('')
        raise e


@click.argument('issue_key')
@cli.command()
@click.pass_obj
def edit(client: JIRAClient, issue_key: str) -> None:
    """Edit issue description"""
    issue = client.get_issue(issue_key)
    description = click.edit(issue.description)

    assert issue.description
    if description is not None and description.strip() != issue.description.strip():
        try:
            client.edit_issue(issue_key, {'description': description.strip()})
            click.echo(
                'Okay, the description for {} has been updated.'.format(issue_key)
            )
        except Exception as e:
            click.echo('There was an issue saving the new description:')
            click.echo(description)
            click.echo('')
            raise e


@click.argument('attachments', type=click.File('rb'), nargs=-1)
@click.argument('issue_key')
@cli.command()
@click.pass_obj
def attach(client: JIRAClient, issue_key: str, attachments) -> None:
    """Attach file(s) to an issue"""

    if len(attachments) == 0:
        click.echo('No attachments to upload')
        return

    for fp in attachments:
        attachments = client.attach(issue_key, fp)

        for attachment in attachments:
            print(f'Attachment {attachment.filename} uploaded.')


@click.argument('summary')
@click.argument('project', metavar='<key>')
@click.option('--type', '-t', required=True)
@click.option('--component', '-c', multiple=True, help='Adds a component')
@click.option('--label', multiple=True, help='Adds a label')
@click.option('--priority', '-p', help='Sets the issue priority')
@click.option('--description', help='Sets the issue description')
@cli.command()
@click.pass_obj
def create(client, project, summary, type, component, label, priority, description):
    """
    Create a new issue, prompting for description contents

    Example:

    \b
        goji create ENG 'Update installation guide' \\
            --type 'Task' \\
            --component Handbook --component External \\
            --priority Low
    """

    if description is None:
        description = click.edit()

    if description is not None:
        fields = {
            'summary': summary,
            'description': description,
            'project': {'key': project},
        }

        if len(component) > 0:
            fields['components'] = [{'name': x} for x in component]

        if len(label) > 0:
            fields['labels'] = label

        if priority is not None:
            fields['priority'] = {'name': priority}

        if type is not None:
            fields['issuetype'] = {'name': type}

        try:
            issue = client.create_issue(fields)
            click.echo('Issue {} created'.format(issue.key))
        except Exception as e:
            click.echo('Description:\n')
            click.echo(description)
            click.echo('')
            raise e


@cli.command()
@click.pass_obj
def login(base_url: str) -> None:
    """Authenticate with JIRA server"""
    email, password = get_credentials(base_url)
    if email is not None:
        if not click.confirm('This server is already configured. Override?'):
            return

    click.echo('Enter your JIRA credentials')

    email = click.prompt('Email', type=str)
    password = click.prompt('Password', type=str, hide_input=True)

    client = JIRAClient(base_url, auth=(email, password))
    check_login(client)
    set_credentials(base_url, email, password)


@click.argument('type')
@click.argument('outward-issue')
@click.argument('inward-issue')
@click.option('--list-types/--no-list-types', default=False)
@cli.command()
@click.pass_obj
def link(client: JIRAClient, inward_issue: str, outward_issue: str, type: str, list_types: bool) -> None:
    if list_types:
        types = client.get_issue_link_types()
        for link_type in types:
            print(f'{link_type.name} ({link_type.inward} -> {link_type.outward})')
        return

    client.link_issue(inward_issue, outward_issue, type)
    print(f'{inward_issue} linked to {outward_issue}')


@click.argument('query')
@click.option('--limit', type=int)
@click.option('--format', default='{key} {summary}')
@click.option('--count', is_flag=True, help='Return the count of matched issues')
@click.option('--all', is_flag=True, help='Return all pages of issues')
@cli.command()
@click.pass_obj
def search(client: JIRAClient, all: bool, count: bool, format: str, limit: Optional[int], query: str) -> None:
    """Search issues using JQL"""

    if count:
        results = client.search(query, fields=['key'], max_results=1)
        print(results.total)
        return

    formatter = Formatter()
    fields = [v[1] for v in formatter.parse(format) if v[1]]

    if all:
        issues = client.search_all(query, fields=fields)
    else:
        issues = client.search(query, fields=fields, max_results=limit).issues

    for issue in issues:
        format_kwargs = dict(
            key=issue.key,
            summary=issue.summary,
            description=issue.description,
            creator=issue.creator,
            assignee=issue.assignee,
            status=issue.status,
            resolution=issue.resolution,
        )

        if 'key' in fields and not isinstance(sys.stdout, io.TextIOWrapper) and isatty(sys.stdout.fileno()):
            url = urljoin(client.base_url, 'browse/%s' % issue.key)
            format_kwargs['key'] = f'\033]8;;{url}\a{issue.key}\033]8;;\a'

        format_kwargs.update(issue.customfields)

        click.echo(format.replace('\\n', '\n').format(**format_kwargs))


@cli.group('sprint')
def sprint() -> None:
    pass


@sprint.command('create')
@click.argument('board_id', envvar='GOJI_BOARD_ID', type=int)
@click.argument('name')
@click.option('--start', type=Datetime(format='%d/%m/%y'), default=None)
@click.option('--end', type=Datetime(format='%d/%m/%y'), default=None)
@click.pass_obj
def sprint_create(client: JIRAClient, board_id: int, name: str, start, end) -> None:
    """Create a sprint"""

    client.create_sprint(board_id, name, start_date=start, end_date=end)
    click.echo('Sprint created')


# Support for plugins, this API is somewhat unstable, it may change between versions.
def add_plugin_command(plugin, main):
    @cli.command(
        name=getattr(plugin, '__name__'),
        help=getattr(plugin, '__doc__'),
        context_settings=dict(
            ignore_unknown_options=True,
        ),
    )
    @click.pass_obj
    @click.argument('args', nargs=-1, type=click.UNPROCESSED)
    def func(client: JIRAClient, args):
        main(client, args)


plugins = [name for _, name, _ in pkgutil.iter_modules() if name.startswith('goji_')]
for module in plugins:
    try:
        plugin = importlib.import_module(module)
        main = partial(getattr(plugin, '__main__'))
        add_plugin_command(plugin, main)
    except Exception as e:
        print(f'Failed to load plugin {module}: {repr(e)}', file=sys.stderr)
        continue
