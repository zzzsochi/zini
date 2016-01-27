from datetime import datetime, timezone, timedelta

import pytest

from zini import Section, SectionParser, ParseError


@pytest.mark.parametrize(
    'l, k, v', [
        ('b = true', 'b', True),
        ('bool = false', 'bool', False),
        ('integer = 13', 'integer', 13),
        ('set float = 3.14', 'set float', 3.14),
        ('str-ing = "string"', 'str-ing', 'string'),
        ("str-ing = 'string'", 'str-ing', 'string'),
        ("dt = 2005-01-13T18:00", 'dt', datetime(2005, 1, 13, 18, 0)),
        ("dt = 2005-01-13T18:00Z", 'dt',
            datetime(2005, 1, 13, 18, 0, tzinfo=timezone.utc)),
        ("dt = 2005-01-13T18:00:10Z", 'dt',
            datetime(2005, 1, 13, 18, 0, 10, tzinfo=timezone.utc)),
        ("dt = 2005-01-13 18:00:10Z", 'dt',
            datetime(2005, 1, 13, 18, 0, 10, tzinfo=timezone.utc)),
        ("dt = 2005-01-13", 'dt', datetime(2005, 1, 13)),
        ("td = 20m", 'td', timedelta(minutes=20)),
        ("td = 2h13s", 'td', timedelta(hours=2, seconds=13)),
    ])
def test_parse_keyvalue(l, k, v):
    s = Section()
    sp = SectionParser(s, 'name')

    key, value = sp._parse_keyvalue(1, l)

    assert key == k
    assert value == v
    assert isinstance(value, type(v))


@pytest.mark.parametrize(
    'l', [
        "k = [13]",
        "k = 13;",
        "k = 1 3",
        "k = '13",
        "k = '13\"",
        "k = '1",
        "k = 1'",
        "k = '",
        "k=v = 13",
        "k = ",
        "= v",
        "k = 2005-01-13Z",
        "k = 2005-13-01",
        "k = 2005-01-13 15:00:05Z+03",
        "k = 2y2d",
        "k = 2d100ss",
    ])
def test_parse_bad_keyvalue(l):
    s = Section()
    sp = SectionParser(s, 'name')

    with pytest.raises(ParseError):
        sp._parse_keyvalue(1, l)


def test_parse_keyvalue_w_scheme():
    s = Section()
    sp = SectionParser(s, 'name')

    s['k'] = 13
    key, value = sp._parse_keyvalue(1, "k = 3")
    assert value == 3


def test_parse_bad_keyvalue_w_scheme():
    s = Section()
    sp = SectionParser(s, 'name')

    s['k'] = 3.14
    with pytest.raises(ParseError):
        sp._parse_keyvalue(1, "k = 3")
