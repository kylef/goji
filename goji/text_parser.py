import re
from typing import List

BOLD_PATTERN = re.compile(r'\*([^\*\n]*)\*')
EMPHASIS_PATTERN = re.compile(r'_([^_]*)_')
COLOR_PATTERN = re.compile(r'{color:([^}]*)}(.*){color}')
LINK_PATTERN = re.compile(r'\[([^|]*)\|([^\]]*)\]')
NOFORMT_PATTERN = re.compile(r'{noformat}(.*){noformat}')
TEXT_EFFECT_PATTERNS = re.compile(
    r'({noformat}.*{noformat}|{color:[^}]*}.*{color}|\*[^\*\n]*\*|_[^_]*_|\[[^|]*\|[^\]]*\])'
)


class Node:
    pass


class Text(Node):
    def __init__(self, value: str):
        self.value = value

    def __repr__(self) -> str:
        return f'<Text {self.value}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Text) and self.value == other.value


class Bold(Node):
    @classmethod
    def pattern(cls):
        return BOLD_PATTERN

    def __init__(self, value: str):
        self.value = value

    def __repr__(self) -> str:
        return f'<Bold {self.value}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Bold) and self.value == other.value


class Emphasis(Node):
    @classmethod
    def pattern(cls):
        return EMPHASIS_PATTERN

    def __init__(self, value: str):
        self.value = value

    def __repr__(self) -> str:
        return f'<Emphasis {self.value}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Emphasis) and self.value == other.value


class Color(Node):
    @classmethod
    def pattern(cls):
        return COLOR_PATTERN

    def __init__(self, color: str, value: str):
        self.color = color
        self.value = value

    def __repr__(self) -> str:
        return f'<Color({self.color}) {self.value}>'

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Color)
            and self.color == other.color
            and self.value == other.value
        )


class Link(Node):
    @classmethod
    def pattern(cls):
        return LINK_PATTERN

    def __init__(self, url: str, value: str):
        self.url = url
        self.value = value

    def __repr__(self) -> str:
        return f'<Link({self.url}) {self.value}>'

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Link)
            and self.url == other.url
            and self.value == other.value
        )


def parse_text_effect(value: str) -> Node:
    match = NOFORMT_PATTERN.match(value)
    if match:
        return Text(match.group(1))

    match = Bold.pattern().match(value)
    if match:
        return Bold(match.group(1))

    match = Emphasis.pattern().match(value)
    if match:
        return Emphasis(match.group(1))

    match = Color.pattern().match(value)
    if match:
        return Color(match.group(1), match.group(2))

    match = Link.pattern().match(value)
    if match:
        return Link(match.group(2), match.group(1))

    return Text(value)


def parse(value: str) -> List[Node]:
    """
    https://jira.atlassian.com/secure/WikiRendererHelpAction.jspa?section=all
    """

    return list(
        map(
            parse_text_effect,
            filter(lambda t: len(t) != 0, TEXT_EFFECT_PATTERNS.split(value)),
        )
    )
