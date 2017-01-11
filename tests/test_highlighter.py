#

import pytest
from sdsc import highlight


@pytest.mark.parametrize("tokens,start,end,expected",
 (
   # 1 - already split
   (["highlight", "these", "two", "words"], 1, 2,
     "highlight <highlight>these two</highlight> words"
    ),
   # 2 - still needs to be split
   ("highlight these two words", 1, 2,
    "highlight <highlight>these two</highlight> words"),
   # 3 - longer example
   (["highlight", "the", "next", "few", "of", "these", "superbly", "chosen", "and", "well-intentioned", "words"], 5, 7,
    "highlight the next few of <highlight>these superbly chosen</highlight> and well-intentioned words"),
   # 4 - example where highlight is out-of-bounds (end)
   ("highlight the next few of these superbly chosen and well-intentioned words", 5, 25,
    "highlight the next few of <highlight>these superbly chosen and well-intentioned words</highlight>"),
   # 5 - example where highlight is out-of-bounds (start)
   ("highlight the first word", -4, 0,
    "<highlight>highlight</highlight> the first word"),
 )
)
def test_highlighter(tokens, start, end, expected):
    """checks whether the highlight function works"""
    assert highlight(tokens, start, end) == expected
