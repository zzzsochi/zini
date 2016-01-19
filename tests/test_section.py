import pytest

from zini import Section, V, NOT_SET, ParseError


def test_create_empty():
    s = Section()
    assert not s


def test_create():
    s = Section({'a': int})
    assert s
    assert 'a' in s


def test_del():
    s = Section()
    s['a'] = int
    assert s
    del s['a']
    assert not s


@pytest.mark.parametrize('t', [bool, int, float, str])
def test_set_type(t):
    s = Section()
    s['a'] = t
    assert s
    assert isinstance(s['a'], V)
    assert s['a'].type is t
    assert s['a'].default is NOT_SET


@pytest.mark.parametrize(
    'v, t',
    [(True, bool), (13, int), (3.14, float), ("string", str)])
def test_set_value(v, t):
    s = Section()
    s['a'] = v

    assert s
    assert isinstance(s['a'], V)
    assert s['a'].type is t
    assert s['a'].default == v


@pytest.mark.parametrize('t', [Section, list, dict])
def test_set_bad_type(t):
    s = Section()

    with pytest.raises(TypeError):
        s['a'] = t


@pytest.mark.parametrize('v', [Section(), list(), dict()])
def test_set_bad_value(v):
    s = Section()

    with pytest.raises(TypeError):
        s['a'] = v


def test_set_bad_key():
    s = Section()

    with pytest.raises(TypeError):
        s[13] = int


@pytest.mark.parametrize(
    'l, k, v, t', [
        ('b = true', 'b', True, bool),
        ('bool = false', 'bool', False, bool),
        ('integer = 13', 'integer', 13, int),
        ('set float = 3.14', 'set float', 3.14, float),
        ('str-ing = "string"', 'str-ing', 'string', str),
        ("str-ing = 'string'", 'str-ing', 'string', str),
    ])
def test_parse_keyvalue(l, k, v, t):
    s = Section()

    key, value = s._parse_keyvalue(1, l)

    assert key == k
    assert value == v
    assert isinstance(value, t)


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
    ])
def test_parse_bad_keyvalue(l):
    s = Section()

    with pytest.raises(ParseError):
        s._parse_keyvalue(1, l)


def test_parse_keyvalue_w_scheme():
    s = Section()
    s['k'] = 13
    key, value = s._parse_keyvalue(1, "k = 3")
    assert value == 3


def test_parse_bad_keyvalue_w_scheme():
    s = Section()
    s['k'] = 3.14
    with pytest.raises(ParseError):
        s._parse_keyvalue(1, "k = 3")
