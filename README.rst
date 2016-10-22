====
Zini
====

.. image:: https://travis-ci.org/zzzsochi/zini.svg?branch=master
    :target: https://travis-ci.org/zzzsochi/zini
    :align: right

.. image:: https://coveralls.io/repos/github/zzzsochi/zini/badge.svg?branch=master
    :target: https://coveralls.io/github/zzzsochi/zini?branch=master
    :align: right


INI-files parser with schemes and types

------------------
Philosophy of Zini
------------------

Application's settings must be simple!
In it should be a code or complex structures. Must be only a simple types.


----------
Why not...
----------

`JSON <http://www.json.org/>`_?
-------------------------------

JSON is uncomfortable and unextendable.


`YAML <http://www.yaml.org/>`_?
-------------------------------

The YAML is like a garden of rakes. It's very complex format.
I do not need all it's futures.


`Configparser <https://docs.python.org/3/library/configparser.html>`_?
----------------------------------------------------------------------

1. Configparser is ugly;
2. Configparser is overengineered;
3. Configparser is not have type casting;
4. Configparser is not have type checking;
5. Configparser is... configparser.


---------------
Supported types
---------------

:boolean: simple ``true`` or ``false``, e.g. ``key = true``
:int: simple numeric type, e.g. ``key = 13``
:float: float type, e.g. ``key = 3.14``
:string: strings *always* uses quotes, e.g. ``key = "some string"``
:datetime: datetime formated like as ISO 8601

    * ``YYYY-MM-DD``
    * ``YYYY-MM-DD hh:mm``
    * ``YYYY-MM-DD hh:mm:ss``
    * ``YYYY-MM-DD hh:mm:ss.sss``

    When the time, you can set timezone as ``Z`` or ``±hh:mm``.

    E.g.:

    * ``key = 2005-01-13``
    * ``key = 2005-01-13 18:05:00``
    * ``key = 2005-01-13 15:05:00 +03:00``
    * ``key = 2005-01-13 15:00Z``


:timedelta: durations:

    * ``key = 20m`` — 20 minutes
    * ``key = 10h2m`` — 10 hours and 2 minutes
    * ``key = 1w2s`` — one week (7 days) and 2 seconds
    * ``key = 1s20ms`` — one 2 second and 20 milliseconds
    * ``key = 1w1d1h1m1s1ms`` — 694861001 milliseconds

:list: list of values:

    .. code:: ini

        key =
            "string value"
            2005-01-13 18:00:05
            13

--------
Examples
--------

``$ cat tests/test.ini``

.. code:: ini

    # first comment
    [first]
    boolean = false
    integer = 13

    [second]
    ; second comment
    boolean = true
    string = "some string"

    [complex]
    list =
        "string"
        "string too"
        "else string"

Simple reading
--------------

.. code:: python

    >>> from zini import Zini
    >>> ini = Zini()
    >>> result = ini.read('tests/test.ini')
    >>> isinstance(result, dict)
    True
    >>> result['first']['boolean'] is False  # automatic type casting
    True
    >>> result['first']['integer'] == 13
    True
    >>> result['second']['string'] == "some string"
    True
    >>> result['complex']['list'] == ["string", "string too", "else string"]
    True

Types and defaults
------------------

.. code:: python

    >>> from zini import Zini
    >>> ini = Zini()
    >>> ini['first']['integer'] = str  # set type
    >>> result = ini.read('tests/test.ini')
    zini.ParseError: error in line 3: 'integer = 13'

.. code:: python

    >>> from zini import Zini
    >>> ini = Zini()
    >>> ini['second']['boolean'] = "string"  # set type and default value
    >>> result = ini.read('tests/test.ini')
    zini.ParseError: error in line 7: 'boolean = true'


Lists of values
~~~~~~~~~~~~~~~

.. code:: python

    >>> import zini
    >>> ini = zini.Zini()
    >>> ini['third']['generic'] = [str]
    >>> result = ini.read('tests/test.ini')
    ParseError: error in line 20: '    10'

