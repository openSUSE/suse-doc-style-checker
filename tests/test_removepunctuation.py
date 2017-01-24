#

import pytest
from sdsc.textutil import removepunctuation


# TODO: Maybe add another parametrize for punctuation characters
@pytest.mark.parametrize("end",   [True, False])
@pytest.mark.parametrize("start", [True, False])
@pytest.mark.parametrize("data", [
    # 0 - no quotes
    'word',
    # 1 - single quote at the start
    '¸word',
    # 2 - single quote at the end
    'word\'',
    # 3 - single quotes at both ends
    '\'word\'',
    # 4 - double quotes at the start
    "\"word",
    # 5 - double quotes at the end
    'word"',
    # 6 - double quotes at both ends
    '"word"',
])
def test_removepunctuation(data, start, end):

    result = "word"
    # For the time being, we check with .isalpha() to cover
    # all punctuation. However, "@".isalpha() would return False
    if start and not data[0].isalpha():
            result = data[0] + result

    if end and not data[-1].isalpha():
            result = result + data[-1]

    removepunctuation(data, start, end) == result