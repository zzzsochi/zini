import os

import pytest

from zini import Zini, Section, V, ParseError


def test_create_empty():
    z = Zini()
    assert not z


def test_create():
    z = Zini(s={'i': int, 's': 'str'})
    assert z
    assert 's' in z
    assert isinstance(z['s'], Section)
    assert len(z['s']) == 2


def test_get_not_exist():
    z = Zini()
    s = z['sect']
    assert isinstance(s, Section)
    assert not s
    assert z


def test_del():
    z = Zini()
    z['sect']['a'] = int
    assert z
    del z['sect']
    assert not z


def test_set():
    z = Zini()
    z['s']['i'] = 13
    assert isinstance(z['s']['i'], V)
    assert z['s']['i'].type is int
    assert z['s']['i'].default == 13


def test_set_bad_key():
    z = Zini()

    with pytest.raises(TypeError):
        z[3]['i'] = 13


def test_set_bad_value():
    z = Zini()

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

    z = Zini(first={'def': 111}, second={'boolean': False})
    res = z.parse(content)
    assert z.content
    assert res is z.result
    assert res == {
        'first': {'boolean': False, 'def': 111, 'integer': 13},
        'second': {'boolean': True, 'string': 'some string'},
    }


def test_parse_already():
    content = """\
[first]
boolean = false
integer = 13
"""
    z = Zini()
    z.parse(content)

    with pytest.raises(ValueError):
        z.parse(content)


def test_parse_bad_first_section_place():
    content = """\
boolean = false
[first]
integer = 13
"""
    z = Zini()

    with pytest.raises(ParseError):
        z.parse(content)


def test_parse_bad_indentation():
    content = """\
[first]
  boolean = false
  integer = 13
"""
    z = Zini()

    with pytest.raises(ParseError):
        z.parse(content)


def test_parse_bad_keyvalue():
    content = """\
[first]
boolean = false
integer: 13
"""
    z = Zini()

    with pytest.raises(ParseError):
        z.parse(content)


def test_read():
    d = os.path.dirname(__file__)
    path = os.path.join(d, 'test.ini')

    z = Zini(first={'def': 111}, second={'boolean': False})
    res = z.read(path)
    assert z.file_name == path
    assert z.content
    assert res is z.result
    assert res == {
        'first': {'boolean': False, 'def': 111, 'integer': 13},
        'second': {'boolean': True, 'string': 'some string'},
    }


def test_read_bad():
    d = os.path.dirname(__file__)
    path = os.path.join(d, 'test-bad.ini')

    z = Zini(first={'def': 111}, second={'boolean': False})
    with pytest.raises(ParseError):
        z.read(path)


def test_read_already():
    d = os.path.dirname(__file__)
    path = os.path.join(d, 'test.ini')

    z = Zini(first={'def': 111}, second={'boolean': False})
    z.read(path)

    with pytest.raises(ValueError):
        z.read(path)


def test_repr():
    z = Zini(first={'def': 111}, second={'boolean': False})
    assert '111' in repr(z)
