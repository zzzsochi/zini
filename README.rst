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
.. :datetime:
.. :timedelta:


-------
Example
-------

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
