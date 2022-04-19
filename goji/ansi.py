from goji.text_parser import Bold, Color, Emphasis, Link, Text, parse

ANSI_FOREGROUND_COLOR = {
    'red': '31',
    'green': '32',
}


def text_formatting_to_ansi(value: str) -> str:
    result = ''

    for node in parse(value):
        if isinstance(node, Text):
            result += node.value
        elif isinstance(node, Bold):
            result += f'\x1b[1m{node.value}\x1b[0m'
        elif isinstance(node, Emphasis):
            result += f'\x1b[3m{node.value}\x1b[0m'
        elif isinstance(node, Color):
            if node.color in ANSI_FOREGROUND_COLOR:
                result += (
                    f'\x1b[{ANSI_FOREGROUND_COLOR[node.color]}m{node.value}\x1b[0m'
                )
            else:
                result += node.value
        elif isinstance(node, Link):
            result += f'\x1b]8;;{node.url}\a{node.value}\x1b]8;'

    return result
