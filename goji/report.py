import importlib
from collections import Counter
from typing import Any, Dict, Optional, List
from urllib.parse import urljoin

import toml

from goji.client import JIRAClient
from goji.models import Issue

HTML_ESCAPE_DICT = {
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
    '"': '&quot;',
    "'": '&#39;',
}


CSS = '''
body {
  --background-color: #f1f1f1;
  --foreground-color: rgb(62, 67, 73);
  --secondary-color: #e9ecef;
}

body {
  font-family: Georgia, serif;
  font-size: 1rem;
  line-height: 1.4;

  padding: 30px;

  background: var(--background-color);
  color: var(--foreground-color);
}

@media screen and (max-width: 680px) {
  body { padding: 10px; }
}

::selection {
  background: var(--secondary-color);
}

main {
  max-width: 750px;
  overflow-wrap: break-word;
}

/* Inline Text */

a {
  color: var(--foreground-color);
  text-decoration: none;
  border-bottom: 1px solid var(--foreground-color);
}

a:hover {
  background: var(--foreground-color);
  color: var(--background-color);
  border-bottom: 1px solid var(--background-color);
}

/* Table */

table {
  width: 100%;
  max-width: 100%;
  margin-bottom: 1rem;
  background-color: transparent;
}

thead th {
  vertical-align: bottom;
  border-bottom: 2px solid #dee2e6;
}

th {
  padding: .75rem;
  vertical-align: top;
  border-top: 1px solid #dee2e6;
  box-sizing: border-box;
  text-align: left;
}

td {
  padding: .75rem;
  border-bottom: 1px solid #dee2e6;
}
'''


def html_escape(text: str) -> str:
    for escape in HTML_ESCAPE_DICT:
        text = text.replace(escape, HTML_ESCAPE_DICT[escape])

    return text


class Widget:
    @classmethod
    def from_config(cls, client: JIRAClient, config: Dict[str, Any], **kwargs):
        title = config.pop('title', None)

        if len(config) != 0:
            keys = ', '.join(config.keys())
            raise ValueError(f'Unknown fields {keys}')

        return cls(client, title, **kwargs)

    def __init__(self, client: JIRAClient, title: Optional[str]):
        self.client = client
        self.title = title

    def render(self, output) -> None:
        pass


class ReportWidget(Widget):
    def __init__(self, title: str, widgets):
        self.title = title
        self.widgets = widgets

    def render(self, output) -> None:
        output.write('<html>')
        output.write('<head>')
        output.write(f'<style>{CSS}</style>')
        output.write('</head>')
        output.write('<body>')
        output.write('<main>')
        output.write('<h1>Report</h1>')

        for widget in self.widgets:
            widget.render(output)

        output.write('</main>')
        output.write('</body>')
        output.write('</html>')


class IssueListWidget(Widget):
    @classmethod
    def from_config(cls, client: JIRAClient, config: Dict[str, Any], **kwargs):
        kwargs['fields'] = config.pop('fields', ['key'])
        return super().from_config(client, config, **kwargs)

    def __init__(self, client: JIRAClient, title: Optional[str], fields: List[str], issues: List[Issue]):
        self.fields = fields
        self.issues = issues
        super().__init__(client, title)

    def render(self, output) -> None:
        title = self.title or 'Search'
        output.write(f'<h2>{html_escape(title)}</h2>')
        output.write('<table>')

        # Header
        output.write('<thead><tr>')
        for field in self.fields:
            output.write(f'<th>{html_escape(field)}</th>')
        output.write('</tr></thead>')

        # Rows
        output.write('<tbody>')
        for issue in self.issues:
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
        output.write('</tbody>')

        output.write('</table>')


class SearchWidget(IssueListWidget):
    @classmethod
    def from_config(cls, client: JIRAClient, config: Dict[str, Any], **kwargs):
        query = config.pop('query', '')
        kwargs['issues'] = list(client.search_all(query=query, fields=config['fields']))
        return super().from_config(client, config, **kwargs)


class StatisticsWidget(Widget):
    @classmethod
    def from_config(cls, client: JIRAClient, config: Dict[str, Any], **kwargs):
        kwargs['query'] = config.pop('query', '')
        kwargs['statistic_type'] = config.pop('statistic_type', '')
        kwargs['results'] = config.pop('results', 10)
        return super().from_config(client, config, **kwargs)

    def __init__(
        self,
        client: JIRAClient,
        title: Optional[str],
        query: str,
        statistic_type: str,
        results: int,
    ):
        self.query = query
        self.statistic_type = statistic_type
        self.results = results
        super().__init__(client, title)

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


def create_widget(client, config) -> Widget:
    widget_type = config['type']
    del config['type']

    if widget_type in WIDGETS:
        widget_cls = WIDGETS[widget_type]
    else:
        module, _, cls_name = widget_type.rpartition('.')
        widget_cls = getattr(importlib.import_module(module), cls_name)

    return widget_cls.from_config(client, config)


def generate_report(client: JIRAClient, input) -> Widget:
    config = toml.load(input)
    return ReportWidget(
        'Report', [create_widget(client, cfg) for cfg in config['widget']]
    )
