import sys

import click
from click_datetime import Datetime
import requests
from requests.compat import urljoin

from goji.client import JIRAClient
from goji.auth import get_credentials, set_credentials


def submit_form(session, response, data=None):
    from requests_html import HTML
    html = HTML(url=response.url, html=response.text)

    forms = html.find('form')
    if len(forms) == 0:
        raise Exception('Page does have any forms')

    form = forms[0]
    url = form.attrs['action']
    fields = form.find('input')

    data = data or {}

    for field in fields:
        name = field.attrs['name']

        if name not in data:
            value = field.attrs['value']
            data[name] = value

    response = session.post(urljoin(response.url, url), data=data)
    return response


def check_login(client):
    response = client.get('myself', allow_redirects=False)

    if response.status_code == 302:
        if sys.version_info.major == 2:
            raise click.ClickException('JIRA instances requires SSO login. goji requires Python 3 to do this. Please upgrade to Python 3')

        # JIRA API may redirect to SSO Authentication if auth fails
        # Manually follow redirect, some SSO requires browser user-agent
        response = client.get(response.headers['Location'], headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        })

        auth = client.session.auth
        client.session.auth = None

        if '<body onLoad="document.myForm.submit()">' in response.text or '<body onLoad="submitForm()">' in response.text:
            # Pretend we're a JavaScript client
            response = submit_form(client.session, response)

        response = submit_form(client.session, response, {
            'ssousername': auth[0],
            'password': auth[1]
        })

        client.save_cookies()

    if response.status_code == 401:
        raise click.ClickException('Incorrect credentials. Try `goji login`.')


@click.group()
@click.option('--base-url', envvar='GOJI_BASE_URL', required=True)
@click.pass_context
def cli(ctx, base_url):
    if not ctx.obj:
        if ctx.invoked_subcommand == 'login':
            ctx.obj = base_url
        else:
            email, password = get_credentials(base_url)

            if not email or not password:
                print('== Authentication not configured. Run `goji login`')
                exit()

            ctx.obj = JIRAClient(base_url, auth=(email, password))

            if len(ctx.obj.session.cookies) > 0:
                check_login(ctx.obj)

@cli.command('whoami')
@click.pass_obj
def open_command(client):
    """View information regarding current user"""
    user = client.get_user()
    print(user)


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


@click.argument('issue_type', required=False)
@click.argument('summary')
@click.argument('project', metavar='<key>')
@click.option('--component', '-c', multiple=True, help='Adds a component')
@click.option('--priority', '-p', help='Sets the issue priority')
@cli.command()
@click.pass_obj
def create(client, issue_type, summary, project, component, priority):
    """
    Create a new issue, prompting for description contents

    Example:

    \b
        goji create ENG 'Update installation guide' 'Task' \\
            --component Handbook --component External \\
            --priority Low
    """
    description = click.edit()
    if description is not None:
        fields = {'summary': summary,
                  'description': description,
                  'project': {'key': project},
                  'components': [{'name': x} for x in component]}
        if priority is not None:
            fields['priority'] = {'name': priority}
        if issue_type is not None:
            fields['issuetype'] = {'name': issue_type}
        issue_key = client.create_issue(fields)
        if issue_key is not None:
            click.echo('Okay, {} created'.format(issue_key))
        else:
            click.echo('There was an issue saving the new issue:')
            click.echo(description)


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

    client = JIRAClient(base_url, auth=(email, password))
    check_login(client)
    set_credentials(base_url, email, password)


@click.argument('query')
@cli.command()
@click.pass_obj
def search(client, query):
    """Search issues using JQL"""
    issues = client.search(query)

    for issue in issues:
        print('{issue.key} {issue.summary}'.format(issue=issue))


@cli.group('sprint')
def sprint():
    pass


@sprint.command('create')
@click.argument('board_id', envvar='GOJI_BOARD_ID', type=int)
@click.argument('name')
@click.option('--start_date', type=Datetime(format='%d/%m/%y'), default=None)
@click.option('--end_date', type=Datetime(format='%d/%m/%y'), default=None)
@click.pass_obj
def sprint_create(client, board_id, name, start_date, end_date):
    """Create a sprint"""
    created = client.create_sprint(board_id, name, start_date=start_date, end_date=end_date)

    if created:
        print('Sprint created')
    else:
        print('Sprint not created')
