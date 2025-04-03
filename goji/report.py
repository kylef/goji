from collections import Counter
import importlib
from typing import Any, Dict
from urllib.parse import urljoin

import toml

from goji.client import JIRAClient


HTML_ESCAPE_DICT = {
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
    '"': '&quot;',
    "'": '&#39;',
}


def html_escape(text: str) -> str:
    for escape in HTML_ESCAPE_DICT:
        text = text.replace(escape, HTML_ESCAPE_DICT[escape])

    return text


class Widget:
    def __init__(self, client: JIRAClient, config: Dict[str, Any]):
        self.client = client
        self.title = config.pop('title', None)

        if len(config) != 0:
            keys = ', '.join(config.keys())
            raise ValueError(f'Unknown fields {keys}')

    def render(self, output) -> None:
        pass


class IssueListWidget(Widget):
    def __init__(self, client: JIRAClient, config: Dict[str, Any]):
        self.client = client
        self.fields = config.pop('fields', ['key'])

        super().__init__(client, config)

    def get_issues(self):
        return NotImplemented

    def render(self, output) -> None:
        title = self.title or 'Search'
        output.write(f'<h2>{html_escape(title)}</h2>')
        output.write('<table>')

        # Header
        output.write('<tr>')
        for field in self.fields:
            output.write(f'<th>{html_escape(field)}</th>')
        output.write('</tr>')

        # Rows
        for issue in self.get_issues():
            output.write('<tr>')
            for field in self.fields:
                if field in issue.customfields:
                    value = issue.customfields[field]
                else:
                    value = getattr(issue, field)

                if field == 'key':
                    url = urljoin(self.client.base_url, f'browse/{issue.key}')
                    output.write(
                        f'<td><a href="{html_escape(url)}">{html_escape(value)}</a></td>'
                    )
                else:
                    output.write(f'<td>{html_escape(value)}</td>')

            output.write('</tr>')

        output.write('</table>')


class SearchWidget(IssueListWidget):
    def __init__(self, client: JIRAClient, config: Dict[str, Any]):
        self.query = config.pop('query')

        super().__init__(client, config)

    def get_issues(self):
        return self.client.search_all(query=self.query, fields=self.fields)


class StatisticsWidget(Widget):
    def __init__(self, client: JIRAClient, config: Dict[str, Any]):
        self.client = client
        self.query = config.pop('query')
        self.statistic_type = config.pop('statistic_type')
        self.results = config.pop('results', 10)

        super().__init__(client, config)

    def get_issues(self):
        if self.statistic_type == 'assignee':
            fields = ['assignee']
        else:
            raise ValueError(f'Unknown statistic type {self.statistic_type}')

        return self.client.search_all(query=self.query, fields=fields)

    def render(self, output) -> None:
        title = self.title or 'Statistics'
        output.write(f'<h2>{html_escape(title)}</h2>')
        output.write('<table>')

        # Header
        output.write('<thead><tr>')
        if self.statistic_type == 'assignee':
            output.write(f'<th>Assignee</th>')
        else:
            raise ValueError(f'Unknown statistic type {self.statistic_type}')
        output.write(f'<th>Count</th>')
        output.write('</tr></thead>')

        counter = Counter()

        for issue in self.get_issues():
            if self.statistic_type != 'assignee':
                raise ValueError(f'Unknown statistic type {self.statistic_type}')

            if issue.assignee is None:
                counter['Unassigned'] += 1
            else:
                counter[issue.assignee] += 1

        # Rows
        output.write('<tbody>')
        for name, count in counter.most_common(self.results):
            output.write('<tr>')
            output.write(f'<td>{html_escape(name)}</td>')
            output.write(f'<td>{html_escape(str(count))}</td>')
            output.write('</tr>')
        output.write('</tbody>')

        output.write('<tfoot>')
        output.write('<tr>')
        output.write(f'<td>Total</td>')
        output.write(f'<td>{html_escape(str(counter.total()))}</td>')
        output.write('</tr>')
        output.write('</tfoot>')

        output.write('</table>')


WIDGETS = {
    'search': SearchWidget,
    'statistics': StatisticsWidget,
}


def generate_report(client: JIRAClient, input, output) -> None:
    config = toml.load(input)
    for config in config['widget']:
        widget_type = config['type']
        del config['type']

        if widget_type in WIDGETS:
            widget = WIDGETS[widget_type](client, config)
        else:
            module, _, cls_name = widget_type.rpartition('.')
            widget_cls = getattr(importlib.import_module(module), cls_name)
            widget = widget_cls(client, config)

        widget.render(output)
