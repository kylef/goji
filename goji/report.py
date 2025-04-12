import importlib
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import toml

from goji.client import JIRAClient
from goji.models import Issue, UserDetails

HTML_ESCAPE_DICT = [
    ('&', '&amp;'),
    ('<', '&lt;'),
    ('>', '&gt;'),
    ('"', '&quot;'),
    ("'", '&#39;'),
]


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
    for escape, replacement in HTML_ESCAPE_DICT:
        text = text.replace(escape, replacement)

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

    def __init__(
        self,
        client: JIRAClient,
        title: Optional[str],
        fields: List[str],
        issues: List[Issue],
    ):
        self.fields = fields
        self.issues = issues
        super().__init__(client, title)

    def get_assignee(self, issue: Issue) -> str:
        if issue.assignee is None:
            return 'Unassigned'

        return issue.assignee.name

    def render(self, output) -> None:
        title = self.title or 'Search'
        output.write(f'<h2>{html_escape(title)}</h2>')
        output.write('<table>')

        # Header
        field_titles = {
            'key': '#',
        }
        output.write('<thead><tr>')
        for field in self.fields:
            field_title = field_titles.get(field, field.capitalize())
            output.write(f'<th>{html_escape(field_title)}</th>')
        output.write('</tr></thead>')

        # Rows
        output.write('<tbody>')
        for issue in self.issues:
            output.write('<tr>')
            for field in self.fields:
                if hasattr(self, f'get_{field}'):
                    value = getattr(self, f'get_{field}')(issue)
                elif field in issue.customfields:
                    value = issue.customfields[field]
                else:
                    value = getattr(issue, field)

                if isinstance(value, datetime):
                    value = value.strftime('%y-%m-%d %H:%M')
                elif isinstance(value, UserDetails):
                    value = value.name
                elif isinstance(value, list):
                    value = ', '.join([str(v) for v in value])

                if field == 'key':
                    url = urljoin(self.client.base_url, f'browse/{issue.key}')
                    output.write(
                        f'<td><a href="{html_escape(url)}">{html_escape(value)}</a></td>'
                    )
                elif value:
                    output.write(f'<td>{html_escape(str(value))}</td>')
                else:
                    output.write(f'<td></td>')

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
        kwargs['field'] = config.pop('field', '')
        kwargs['results'] = config.pop('results', 10)
        return super().from_config(client, config, **kwargs)

    def __init__(
        self,
        client: JIRAClient,
        title: Optional[str],
        query: str,
        field: str,
        results: int,
    ):
        self.query = query
        self.field = field
        self.results = results
        super().__init__(client, title)

    def get_issues(self):
        return self.client.search_all(query=self.query, fields=[self.field])

    def render(self, output) -> None:
        title = self.title or 'Statistics'
        output.write(f'<h2>{html_escape(title)}</h2>')
        output.write('<table>')

        # Header
        output.write('<thead><tr>')
        output.write(f'<th>{html_escape(self.field.capitalize())}</th>')
        output.write(f'<th>Count</th>')
        output.write('</tr></thead>')

        counter = Counter()

        for issue in self.get_issues():
            value = getattr(issue, self.field)
            if self.field == 'assignee' and value is None:
                value = 'Unassigned'

            if isinstance(value, UserDetails):
                value = value.name

            if self.field == 'labels':
                for label in value:
                    counter[str(label)] += 1
            else:
                counter[str(value)] += 1

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
