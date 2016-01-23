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


V = namedtuple('V', ('type', 'default'))


class ParseError(Exception):
    def __init__(self, n, line):
        super().__init__(n, line)
        self.n = n
        self.line = line

    def __str__(self):  # pragma: no cover
        return "error in line {}: {!r}".format(self.n, self.line)


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
        """ Read a file for parsing
        """
        with open(file_name) as f:
            content = f.read()

        return self.parse(content)

    def parse(self, content):
        """ Parse data from string
        """
        result = {}

        section = None

        for n, line in enumerate(content.split('\n')):
            line = line.rstrip()

            if not line:
                # skip empty
                continue
            elif line[0] in '#;':
                # skip comments
                continue
            elif line.startswith(' '):
                # indentation not allowed for future b/c
                raise ParseError(n, line)
            elif line.startswith('[') and line.endswith(']'):
                # setup section
                section = line[1:-1]
            elif '=' not in line:
                # must be keyvalue
                raise ParseError(n, line)
            elif section is None:
                # first keyvalue is not sector
                raise ParseError(n, line)
            else:
                key, value = self[section]._parse_keyvalue(n, line)
                result.setdefault(section, {})[key] = value

        for name, sector in self.items():
            # set defaults
            for key, v in sector.items():
                if v.default is not NOT_SET:
                    result.setdefault(name, {}).setdefault(key, v.default)

        return result

    @property
    def defaults(self):
        """ Return default values

        Equal of `zini.parse('')`.
        """
        return self.parse('')


class Section(MutableMapping):
    def __init__(self, data=None):
        self._data = {}
        if data is not None:
            for k, v in data.items():
                self[k] = v

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("only strings is allowed for keys")
        elif isinstance(value, type):
            v = V(value, NOT_SET)
        else:
            v = V(type(value), value)

        self._check_type(v.type)

        self._data[key] = v

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

    def _check_type(self, t):
        if t not in [bool, int, float, str, datetime, timedelta]:
            raise TypeError("unknown type: {t.__name__}".format(t=t))

    def _parse_keyvalue(self, n, line):
        key, value = (i.strip() for i in line.split('=', 1))
        if not key or not value:
            raise ParseError(n, line)

        parsers = [
            self._get_bool,
            int, float,
            self._get_str,
            self._get_datetime,
            self._get_timetelta,
        ]

        for func in parsers:
            try:
                value = func(value)
                break
            except ValueError:
                pass
        else:
            raise ParseError(n, line)

        if key in self and not isinstance(value, self[key].type):
            raise ParseError(n, line)
        else:
            return key, value

    @staticmethod
    def _get_bool(value):
        if value.lower() == 'false':
            return False
        elif value.lower() == 'true':
            return True
        else:
            raise ValueError

    @staticmethod
    def _get_str(value):
        if len(value) < 2:
            raise ValueError
        elif ((value[0] == '"' and value[-1] == '"') or
                (value[0] == "'" and value[-1] == "'")):
            return value[1:-1]
        else:
            raise ValueError

    @staticmethod
    def _get_datetime(value):
        if not RE_ISO8601.match(value):
            raise ValueError
        else:
            return dateutil.parser.parse(value)

    @staticmethod
    def _get_timetelta(value):
        res = RE_TIMEDELTA.match(value)
        if not res:
            raise ValueError

        res = {k: int(v) for k, v in res.groupdict().items() if v}
        return timedelta(**res)
