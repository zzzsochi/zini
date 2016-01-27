import pytest

from zini import Section, V, NOT_SET


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
