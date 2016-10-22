from datetime import datetime, timezone, timedelta

import pytest

import zini


@pytest.mark.parametrize(
    'parser, line, value',
    [
        (zini.NoneParser, 'null = none', None),
        (zini.NoneParser, 'null = ', None),
        (zini.BooleanParser, 'b = true', True),
        (zini.BooleanParser, 'bool = false', False),
        (zini.IntegerParser, 'integer = 13', 13),
        (zini.FloatParser, 'set float = 3.14', 3.14),
        (zini.StringParser, 'str-ing = "string"', 'string'),
        (zini.StringParser, "str-ing = 'string'", 'string'),
        (zini.DatetimeParser, "dt = 2005-01-13T18:00",
            datetime(2005, 1, 13, 18, 0)),
        (zini.DatetimeParser, "dt = 2005-01-13T18:00Z",
            datetime(2005, 1, 13, 18, 0, tzinfo=timezone.utc)),
        (zini.DatetimeParser, "dt = 2005-01-13T18:00:10Z",
            datetime(2005, 1, 13, 18, 0, 10, tzinfo=timezone.utc)),
        (zini.DatetimeParser, "dt = 2005-01-13 18:00:10Z",
            datetime(2005, 1, 13, 18, 0, 10, tzinfo=timezone.utc)),
        (zini.DatetimeParser, "dt = 2005-01-13",
            datetime(2005, 1, 13)),
        (zini.TimedeltaParser, "td = 20m",
            timedelta(minutes=20)),
        (zini.TimedeltaParser, "td = 2h13s",
            timedelta(hours=2, seconds=13)),
    ])
def test_parse_one_line(parser, line, value):
    res = parser()([(0, line)])
    assert res == value
    assert type(res) is type(value)

    res = zini.GenericParser()([(0, line)])
    assert res == value
    assert type(res) is type(value)


@pytest.mark.parametrize(
    'line',
    [
        "k = [13]",
        "k = 13;",
        "k = 1 3",
        "k = '13",
        "k = '13\"",
        "k = '1",
        "k = 1'",
        "k = '",
        "k=v = 13",
        "= v",
        "= 13",
        "k = 2005-01-13Z",
        "k = 2005-13-01",
        "k = 2005-01-13 15:00:05Z+03",
        "k = 2y2d",
        "k = 2d100ss",
        "k: 0",
    ])
@pytest.mark.parametrize(
    'parser', [
        zini.StringParser,
        zini.BooleanParser,
        zini.IntegerParser,
        zini.FloatParser,
        zini.DatetimeParser,
        zini.TimedeltaParser,
        zini.GenericParser,
    ]
)
def test_parse_bad_keyvalue(line, parser):
    with pytest.raises(zini.ParseError):
        parser()([(0, line)])


@pytest.mark.parametrize(
    'parser', [
        zini.StringParser,
        zini.BooleanParser,
        zini.IntegerParser,
        zini.FloatParser,
        zini.DatetimeParser,
        zini.TimedeltaParser,
    ]
)
def test_parse_multi_error(parser):
    token = [
        (0, 'key = "value"'),
        (1, '    subkey = 13'),
    ]
    with pytest.raises(zini.ParseError):
        parser()(token)
