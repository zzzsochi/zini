import pytest

import zini


@pytest.mark.parametrize('input, output', [
    (
        [
            (0, 'key0 = value0'),
            (1, 'key1 = value1'),
            (2, 'key2 = value2'),
        ], [
            [
                (0, 'key0 = value0'),
            ],
            [
                (1, 'key1 = value1'),
            ],
            [
                (2, 'key2 = value2'),
            ],
        ]
    ),
    (
        [
            (0, 'key0 = value0'),
            (1, 'key1 = value1'),
            (3, ''),
            (2, 'key2 = value2'),
        ], [
            [
                (0, 'key0 = value0'),
            ],
            [
                (1, 'key1 = value1'),
            ],
            [
                (2, 'key2 = value2'),
            ],
        ]
    ),
    (
        [
            (0, 'key0 = value0'),
            (1, 'key1 ='),
            (2, '  k0 = v0'),
            (3, '  k1 = k1'),
            (4, 'key2 = value2'),
            (5, ''),
        ], [
            [
                (0, 'key0 = value0'),
            ],
            [
                (1, 'key1 ='),
                (2, '  k0 = v0'),
                (3, '  k1 = k1'),
            ],
            [
                (4, 'key2 = value2'),
            ],
        ]
    ),
    (
        [
            (0, 'key0 = value0'),
            (1, 'key1 ='),
            (2, '  k0 = v0'),
            (3, '  k1 ='),
            (4, '    k00 = v00'),
            (5, '  k2 = v2'),
            (6, 'key2 = value2'),
        ], [
            [
                (0, 'key0 = value0'),
            ],
            [
                (1, 'key1 ='),
                (2, '  k0 = v0'),
                (3, '  k1 ='),
                (4, '    k00 = v00'),
                (5, '  k2 = v2'),
            ],
            [
                (6, 'key2 = value2'),
            ],
        ]
    ),
])
def test_tokenize(input, output):
    assert list(zini.tokenize(input)) == output


def test_identation_error():
    lines = [
        (0, 'key0 = 0'),
        (1, '  key1 = 1'),
        (2, ' key2 = 2'),
    ]
    with pytest.raises(zini.ParseError):
        list(zini.tokenize(lines))
