#

import pytest
from sdsc import isDupe
from sdsc.tokens import tokenizer


@pytest.mark.parametrize("tokens,expected",
 (
   # 1
   ("This is a simple sentence.",
    ["This", "is", "a", "simple", "sentence."]),
   # 2
   ("This is a less simple sentence with a\xa0nbsp.",
    ["This", "is", "a", "less", "simple", "sentence", "with", "a", "nbsp."]),
 )
)
def test_tokenizer(tokens, expected):
    """checks whether the tokenizer works as expected"""
    assert tokenizer(tokens) == expected


@pytest.mark.parametrize("tokens,result",
 [
     # 1
     (["this", "is", "a", "test"], 0 ),
     # 2
     (["this", "is", "is", "a", "test"], 1),
     # 3
     (["this", "is", "this", "is", "a", "test"], 2),
     # 4
     (["this", "is", "(this", "is)", "a", "test"], 0),
 ],
)
def test_isDupe(tokens, result):
    """checks whether isDupe is correct"""
    assert isDupe(tokens, 2) == result
