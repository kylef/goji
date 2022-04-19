from goji.text_parser import Bold, Color, Emphasis, Link, Text, parse


def test_parse_text():
    assert parse('value') == [Text('value')]


def test_parse_text_with_list_item():
    assert parse('* value') == [Text('* value')]


def test_parse_text_with_list_items():
    assert parse('* value\n* value') == [Text('* value\n* value')]


def test_parse_bold():
    assert parse('*value*') == [Bold('value')]


def test_parse_emphesis():
    assert parse('_value_') == [Emphasis('value')]


def test_parse_color():
    assert parse('{color:green}value{color}') == [Color('green', 'value')]


def test_parse_link():
    assert parse('[value|https://example.com]') == [
        Link('https://example.com', 'value')
    ]


def test_parse_noformat():
    assert parse('{noformat}*bold* _emphasis_{noformat}') == [Text('*bold* _emphasis_')]


def test_parse_text_effects():
    assert parse(
        '*bold* _emphasis_ {color:green}value{color} [Example|https://example.com]'
    ) == [
        Bold('bold'),
        Text(' '),
        Emphasis('emphasis'),
        Text(' '),
        Color('green', 'value'),
        Text(' '),
        Link('https://example.com', 'Example'),
    ]
