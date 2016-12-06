#

import pytest
from sdsc import highlight


@pytest.mark.parametrize("tokens,start,end,expected",
 (
   # 1
   (["highlight", "these", "two", "words"], 1, 2,
     "highlight <highlight>these two</highlight> words"
    ),
   # 2
   ("highlight these two words", 1, 2,
    "highlight <highlight>these two</highlight> words"),
 )
)
def test_highlighter(tokens, start, end, expected):
    """checks whether the highlight function works"""
    assert highlight(tokens, start, end) == expected
