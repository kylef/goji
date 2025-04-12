from goji.ansi import text_formatting_to_ansi


def test_convert_text():
    assert text_formatting_to_ansi('test text') == 'test text'


def test_convert_bold():
    assert text_formatting_to_ansi('*bold*') == '\x1b[1mbold\x1b[0m'


def test_convert_emphesis():
    assert text_formatting_to_ansi('_emphasis_') == '\x1b[3memphasis\x1b[0m'


def test_convert_color_red():
    assert text_formatting_to_ansi('{color:red}red{color}') == '\x1b[31mred\x1b[0m'


def test_convert_color_green():
    assert (
        text_formatting_to_ansi('{color:green}green{color}') == '\x1b[32mgreen\x1b[0m'
    )


def test_convert_link():
    assert (
        text_formatting_to_ansi('[Example|https://example.com]')
        == '\x1b]8;;https://example.com\aExample\x1b]8;'
    )
