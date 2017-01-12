#

import pytest
import sdsc
@pytest.mark.parametrize("value, result",
  (
    # 0, 1, 2 - simple, correct example
    ('100mm', ('100','mm')),
    # 3, 4, 5 - malformatted example (extra space), error code expected
    ('100 mm', ('MALFORMED_VALUE', 'MALFORMED_VALUE')),
    # 6, 7, 8 - malformatted example (extra *), error code expected
    ('*100mm', ('MALFORMED_VALUE', 'MALFORMED_VALUE')),
    # 9, 10, 11 - malformatted example (extra *), error code expected
    ('100mm*', ('MALFORMED_VALUE', 'MALFORMED_VALUE')),
    # 12, 13, 14 - malformatted example (+ as the unit), error code expected
    ('100+', ('MALFORMED_VALUE', 'MALFORMED_VALUE')),
    # 15, 16, 17 - correct example with %, unit expected
    ('200%', ('200','%')),
    # 18, 19, 20 - example with bad unit %%, error code expected
    ('1%%', ('MALFORMED_VALUE', 'MALFORMED_VALUE')),
    # 21, 22, 23 - example with bad unit remm, error code expected
    ('77.7remm', ('MALFORMED_VALUE', 'MALFORMED_VALUE')),
    # 24, 25, 26 - example with float
    ('77.7rem', ('77.7','rem')),
    # 27, 28, 29 - example without unit
    ('77', ('77','')),
    # 30, 31, 32 - floating point example without unit
    ('91.5', ('91.5','')),
    # 33, 34, 35 - empty string, error code expected
    ('', ('MALFORMED_VALUE', 'MALFORMED_VALUE')),
  )
)
@pytest.mark.parametrize("part",
    ('value', None, 'unit')
)
def test_splitvalueunit(value, part, result):
    """Checks whether values and units are properly split"""
    if part == 'unit':
        result = result[1]
    else:
        result = result[0]
    assert sdsc.splitvalueunit(0, value, part) == result
