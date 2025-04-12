from io import StringIO

import pytest

from goji.client import JIRAClient
from goji.models import Issue
from goji.report import (
    CSS,
    IssueListWidget,
    ReportWidget,
    StatisticsWidget,
    Widget,
    html_escape,
)
from tests.server import JIRAServer


def test_html_escape():
    assert html_escape('<test>') == '&lt;test&gt;'
    assert html_escape('&') == '&amp;'
    assert html_escape('"') == '&quot;'
    assert html_escape("'") == '&#39;'
    assert html_escape('Hello & <World>') == 'Hello &amp; &lt;World&gt;'


def test_create_widget(client: JIRAClient):
    widget = Widget.from_config(client, {'title': 'Test Widget'})

    assert widget.client == client
    assert widget.title == 'Test Widget'


def test_create_widget_unknown_field(client: JIRAClient):
    with pytest.raises(ValueError) as exc:
        Widget.from_config(client, {'title': 'Test', 'unknown': 'field'})

    assert str(exc.value) == 'Unknown fields unknown'


def test_report_widget(client: JIRAClient):
    widget1 = Widget(client, "Widget 1")
    widget2 = Widget(client, "Widget 2")
    report = ReportWidget("Test Report", [widget1, widget2])

    output = StringIO()
    report.render(output)

    assert output.getvalue() == (
        '<html>'
        '<head>'
        f'<style>{CSS}</style>'
        '</head>'
        '<body>'
        '<main>'
        '<h1>Report</h1>'
        '</main>'
        '</body>'
        '</html>'
    )


def test_issue_list_widget(client: JIRAClient):
    issues = [
        Issue.from_json(
            {
                'key': 'GOJI-123',
                'fields': {
                    'summary': 'Test Issue',
                    'assignee': {'displayName': 'Test User'},
                    'customfield_10000': 'Custom Value',
                },
            }
        )
    ]

    widget = IssueListWidget(
        client,
        'Test Issues',
        fields=['key', 'summary', 'assignee', 'customfield_10000'],
        display_names={'customfield_10000': 'Custom Field'},
        issues=issues,
    )

    output = StringIO()
    widget.render(output)

    assert output.getvalue() == (
        '<h2>Test Issues</h2>'
        '<table>'
        '<thead><tr>'
        '<th>#</th>'
        '<th>Summary</th>'
        '<th>Assignee</th>'
        '<th>Custom Field</th>'
        '</tr></thead>'
        '<tbody><tr>'
        f'<td><a href="{client.base_url}/browse/GOJI-123">GOJI-123</a></td>'
        '<td>Test Issue</td>'
        '<td>Test User</td>'
        '<td>Custom Value</td>'
        '</tr></tbody>'
        '</table>'
    )


def test_statistics_widget(client: JIRAClient, server: JIRAServer):
    server.set_search_response()
    widget = StatisticsWidget(
        client, 'Test Statistics', '', field='assignee', results=5
    )

    output = StringIO()
    widget.render(output)

    assert output.getvalue() == (
        '<h2>Test Statistics</h2>'
        '<table>'
        '<thead><tr>'
        '<th>Assignee</th>'
        '<th>Count</th>'
        '</tr></thead>'
        '<tbody>'
        '<tr><td>Delisa</td><td>1</td></tr>'
        '</tbody><tfoot><tr><td>Total</td><td>1</td></tr></tfoot></table>'
    )
