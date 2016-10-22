import os

import pytest

import zini


def test_create_empty():
    z = zini.Zini()
    assert not z


def test_create():
    z = zini.Zini(s={'i': int, 's': 'str'})
    assert z
    assert 's' in z
    assert isinstance(z['s'], zini.Section)
    assert len(z['s']) == 2


def test_get_not_exist():
    z = zini.Zini()
    s = z['sect']
    assert isinstance(s, zini.Section)
    assert not s
    assert z


def test_del():
    z = zini.Zini()
    z['sect']['a'] = int
    assert z
    del z['sect']
    assert not z


def test_set():
    z = zini.Zini()
    z['s']['i'] = 13
    assert isinstance(z['s']['i'], zini.IntegerParser)
    assert z['s']['i'].type is int
    assert z['s']['i'].default == 13


def test_set_bad_key():
    z = zini.Zini()

    with pytest.raises(TypeError):
        z[3]['i'] = 13


def test_set_bad_value():
    z = zini.Zini()

    with pytest.raises(TypeError):
        z["k"] = 13


def test_parse():
    content = """\
# first comment
[first]
boolean = false
integer = 13

[second]
; second comment
boolean = true
string = "some string"
"""
    z = zini.Zini(first={'def': 111}, second={'boolean': False})
    res = z.parse(content)
    assert res == {
        'first': {'boolean': False, 'def': 111, 'integer': 13},
        'second': {'boolean': True, 'string': 'some string'},
    }


def test_parse_bad_first_section_place():
    content = """\
boolean = false
[first]
integer = 13
"""
    z = zini.Zini()

    with pytest.raises(zini.ParseError):
        z.parse(content)


def test_parse_bad_keyvalue():
    content = """\
[first]
boolean = false
integer: 13
"""
    z = zini.Zini()

    with pytest.raises(zini.ParseError):
        z.parse(content)


def test_defaults():
    z = zini.Zini()
    z['first']['int'] = 1
    z['first']['str'] = str
    z['second']['int'] = 2
    z['third']['bool'] = bool

    assert z.defaults == {'first': {'int': 1}, 'second': {'int': 2}, 'third': {}}


def test_read():
    d = os.path.dirname(__file__)
    path = os.path.join(d, 'test.ini')

    z = zini.Zini(first={'def': 111}, second={'boolean': False})
    res = z.read(path)
    assert res == {
        'first': {'boolean': False, 'def': 111, 'integer': 13},
        'second': {'boolean': True, 'string': 'some string'},
    }


def test_read_bad():
    d = os.path.dirname(__file__)
    path = os.path.join(d, 'test-bad.ini')

    z = zini.Zini(first={'def': 111}, second={'boolean': False})
    with pytest.raises(zini.ParseError):
        z.read(path)


def test_repr():
    z = zini.Zini(first={'def': 111}, second={'boolean': False})
    assert '111' in repr(z)
