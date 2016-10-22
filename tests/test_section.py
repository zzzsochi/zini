from datetime import datetime

import pytest

import zini


def test_create_empty():
    s = zini.Section()
    assert not s


def test_create():
    s = zini.Section({'a': int})
    assert s
    assert 'a' in s


def test_del():
    s = zini.Section()
    s['a'] = int
    assert s
    del s['a']
    assert not s


@pytest.mark.parametrize('t, parser_class', [
    (bool, zini.BooleanParser),
    (int, zini.IntegerParser),
    (float, zini.FloatParser),
    (str, zini.StringParser),
    (list, zini.ListParser),
])
def test_set_type(t, parser_class):
    s = zini.Section()
    s['a'] = t
    assert s
    assert isinstance(s['a'], parser_class)


def test_set_parser():
    s = zini.Section()
    parser = zini.BooleanParser()
    s['a'] = parser
    assert s['a'] is parser


@pytest.mark.parametrize('value, parser_class', [
    (True, zini.BooleanParser),
    (False, zini.BooleanParser),
    (13, zini.IntegerParser),
    (3.14, zini.FloatParser),
    ("string", zini.StringParser),
    ([], zini.ListParser),
    ([str], zini.ListParser),
    ([int], zini.ListParser),
    ([datetime], zini.ListParser),
])
def test_set_default(value, parser_class):
    s = zini.Section()
    s['a'] = value
    assert s
    assert isinstance(s['a'], parser_class)


@pytest.mark.parametrize('value, item_parser_class', [
    ([], zini.GenericListItemParser),
    ([str], zini.StringParser),
    ([int], zini.IntegerParser),
    ([datetime], zini.DatetimeParser),
])
def test_set_list_item_parser(value, item_parser_class):
    s = zini.Section()
    s['a'] = value
    assert s
    assert isinstance(s['a'], zini.ListParser)
    assert isinstance(s['a'].item_parser, item_parser_class)


@pytest.mark.parametrize('t', [zini.Section, object(), object])
def test_set_bad_type(t):
    s = zini.Section()
    s['a'] = t
    assert isinstance(s['a'], zini.GenericParser)


def test_set_bad_key():
    s = zini.Section()

    with pytest.raises(TypeError):
        s[13] = int
