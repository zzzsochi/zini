from collections.abc import MutableMapping
from collections import namedtuple
from datetime import datetime, timedelta
import re

import dateutil.parser

__version__ = '1.0.2'

NOT_SET = type('NOT_SET', (), {})
RE_ISO8601 = re.compile(
    '^\d\d\d\d-\d\d-\d\d'  # YYYY-MM-DD
    '(?:[\sT]\d\d:\d\d(?::\d\d(?:\.\d+)?)?'  # [\sT]hh:mm:ss.mmm
    '(?:\s?[+-]\d\d(?::\d\d)?)?)?(?:[zZ])?$'  # [+-]hh:mm
)

RE_TIMEDELTA = re.compile(
    '^(?:(?P<weeks>\d+)w)?(?:(?P<days>\d+)d)?'  # w, d
    '(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?'  # h, m
    '(?:(?P<seconds>\d+)s)?(?:(?P<milliseconds>\d+)ms)?$'  # s, ms
)


KeyValue = namedtuple('KeyValue', ('key', 'value'))


class ParseError(Exception):
    def __init__(self, n, line, comment=None):
        super().__init__(n, line)
        self.n = n
        self.line = line
        self.comment = comment

    def __str__(self):  # pragma: no cover
        if self.comment:
            return ("error in line {s.n}: {s.line!r}\n"
                    "{s.comment}".format(s=self))
        else:
            return "error in line {s.n}: {s.line!r}".format(s=self)


class Zini(MutableMapping):
    def __init__(self, **sections):
        self._sections = {}

        for name, data in sections.items():
            self[name] = data

    def __getitem__(self, key):
        section = self._sections.get(key)
        if section is None:
            self[key] = section = Section()

        return section

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("only strings is allowed for sectors name")
        elif isinstance(value, Section):
            self._sections[key] = value
        elif not isinstance(value, dict):
            raise TypeError("only dict or Sector is allowed for sectors")
        else:
            self[key] = Section(value)

    def __delitem__(self, key):
        del self._sections[key]

    def __iter__(self):  # pragma: no cover
        return iter(self._sections)

    def __len__(self):
        return len(self._sections)

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            repr(self._sections),
        )

    def read(self, file_name):
        """ Read a file for parsing.
        """
        with open(file_name) as f:
            content = f.read()

        return self.parse(content)

    def parse(self, content):
        """ Parse data from string.
        """
        result = {}

        lost_section_keys = set(self.keys())
        lines = enumerate(content.split('\n'))

        for section_key, section_token in tokenize_sections(lines):
            lost_section_keys.discard(section_key)
            result[section_key] = self[section_key](section_token)

        for section_key in lost_section_keys:
            result[section_key] = self[section_key].get_defaults()

        return result

    @property
    def defaults(self):
        """ Return default values.

        Equal of `zini.parse('')`.
        """
        return self.parse('')


class Parser:
    def __init__(self, default=NOT_SET):
        self.default = default

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            self.default if self.default is not NOT_SET else "",
        )

    def __call__(self, token):  # pragma: no cover
        self.check(token)
        return get_keyvalue(token).value

    def check(self, token):  # pragma: no cover
        if not token:
            raise ParseError(*token[0])


class OneLineParser(Parser):
    def check(self, token):
        super().check(token)
        if len(token) > 1:
            raise ParseError(*token[1])


class StringParser(OneLineParser):
    def __call__(self, token):
        self.check(token)
        return get_keyvalue(token).value[1:-1]

    def check(self, token):
        super().check(token)
        value = get_keyvalue(token).value

        if len(value) < 2:
            raise ParseError(*token[0])
        elif not (value[0] in '\'\"' and value[0] == value[-1]):
            raise ParseError(*token[0])


class BooleanParser(OneLineParser):
    def __call__(self, token):  # pragma: no cover
        self.check(token)
        value = get_keyvalue(token).value.lower()

        if value == 'false':
            return False
        elif value == 'true':
            return True
        else:
            raise RuntimeError(token)

    def check(self, token):
        super().check(token)
        value = get_keyvalue(token).value.lower()

        if value not in ['false', 'true']:
            raise ParseError(*token[0])


class BaseSimpleParser(OneLineParser):
    type = None

    def __call__(self, token):
        self.check(token)
        return self.type(get_keyvalue(token).value)

    def check(self, token):
        super().check(token)
        value = get_keyvalue(token).value

        try:
            self.type(value)
        except ValueError as exc:
            raise ParseError(*token[0]) from exc


class IntegerParser(BaseSimpleParser):
    type = int


class FloatParser(BaseSimpleParser):
    type = float


class DatetimeParser(OneLineParser):
    def __call__(self, token):
        self.check(token)
        value = get_keyvalue(token).value

        try:
            return dateutil.parser.parse(value)
        except ValueError as exc:
            n, line = token[0]
            raise ParseError(n, line, str(exc)) from exc

    def check(self, token):
        super().check(token)
        value = get_keyvalue(token).value

        if not RE_ISO8601.match(value):
            raise ParseError(*token[0])


class TimedeltaParser(OneLineParser):
    def __call__(self, token):
        self.check(token)
        value = get_keyvalue(token).value

        res = RE_TIMEDELTA.match(value)
        tdelta = {k: int(v) for k, v in res.groupdict().items() if v}
        return timedelta(**tdelta)

    def check(self, token):
        super().check(token)
        value = get_keyvalue(token).value

        res = RE_TIMEDELTA.match(value)
        if not (res and [i for i in res.groups() if i]):
            raise ParseError(*token[0])


class GenericParser(Parser):
    parsers = [
        StringParser,
        BooleanParser,
        IntegerParser,
        FloatParser,
        DatetimeParser,
        TimedeltaParser,
    ]

    def __call__(self, token):
        self.check(token)
        for parser in self.parsers:
            try:
                return parser()(token)
            except ParseError:
                pass
        else:
            raise ParseError(*token[0])

    def check(self, token):
        for parser in self.parsers:
            try:
                parser().check(token)
                return
            except ParseError:
                pass
        else:
            raise ParseError(*token[0])


class Section(MutableMapping):
    default_parser_class = GenericParser

    parsers = [
        (str, StringParser),
        (bool, BooleanParser),
        (int, IntegerParser),
        (float, FloatParser),
        (datetime, DatetimeParser),
        (timedelta, TimedeltaParser),
    ]

    def __init__(self, data=None):
        self._data = {}
        if data:
            for k, v in data.items():
                self[k] = v

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("only strings is allowed for keys")
        elif isinstance(value, Parser):
            self._data[key] = value
        else:
            self._data[key] = self.get_parser(value)

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):  # pragma: no cover
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            repr(self._data),
        )

    def __call__(self, lines):
        result = self.get_defaults()

        for token in tokenize(lines):
            key = get_key(token)

            if key in self:
                parser = self[key]
            else:
                parser = self.default_parser_class()

            result[key] = parser(token)

        return result

    def get_parser(self, value):
        if isinstance(value, type):
            check = issubclass
        else:
            check = isinstance

        for t, parser in self.parsers:
            if check(value, t):
                if isinstance(value, type):
                    return parser()
                else:
                    return parser(value)
        else:
            return self.default_parser_class(value)

    def get_defaults(self):
        defaults = {}

        for key, parser in self.items():
            if parser.default is not NOT_SET:
                defaults[key] = parser.default

        return defaults


def tokenize_sections(lines):
    lines = ((n, l.rstrip()) for n, l in lines)

    for n, line in lines:

        if not line:
            continue
        elif line and line[0] in '#;':
            continue
        elif line.startswith('[') and line.endswith(']'):
            section_key = line[1:-1]
            break
        else:
            raise ParseError(n, line)
    else:
        return

    section_token = []
    for n, line in lines:
        if line and line[0] in '#;':
            continue
        if line.startswith('[') and line.endswith(']'):
            if section_token:
                yield section_key, section_token

            section_key = line[1:-1]
            section_token = []
        else:
            section_token.append((n, line))
    else:
        if section_token:
            yield section_key, section_token


def tokenize(lines):
    lines = lines.copy()

    while lines:
        n, line = lines.pop(0)
        if not line.strip():
            continue

        token_indent = get_indent(line)
        token = [(n, line)]

        if len(lines) > 1:
            block_indent = get_indent(lines[0][1])

            if block_indent > token_indent:
                while lines:
                    n, line = lines[0]
                    if line.strip():
                        indent = get_indent(line)
                    else:
                        indent = block_indent

                    if indent <= token_indent:
                        break
                    elif token_indent < indent < block_indent:
                        raise ParseError(n, line)
                    elif indent >= block_indent:
                        token.append((n, line))
                        del lines[0]
                    else:  # pragma: no cover
                        raise RuntimeError(n, line)

        if token:
            yield token


def get_key(token):
    n, line = token[0]

    if '=' in line:
        return line.split('=', 1)[0].strip()
    else:
        raise ParseError(n, line)


def get_keyvalue(token):
    if not token:  # pragma: no cover
        raise ValueError(token)

    n, line = token[0]

    if '=' not in line:
        raise ParseError(n, line)

    key, value = (i.strip() for i in line.split('=', 1))
    if not key:
        raise ParseError(n, line)

    return KeyValue(key, value)


def get_indent(value):
    if not value:
        return 0

    for n, char in enumerate(value):
        if char != ' ':
            break

    return n
