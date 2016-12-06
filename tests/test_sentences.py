#

import pytest
from sdsc import sentencesegmenter


@pytest.mark.parametrize("sentence,expected",
(
   # 1
   ("This is a simple ##@command-2## sentence. This one too.",
    ["This is a simple ##@command-2## sentence", "This one too"]),
   # 2
   ("This is not a test in one go. openSUSE is not written with a capital letter.",
    ["This is not a test in one go",
     "openSUSE is not written with a capital letter"]),
   # 3
   ("This is a sentence, e.g. for me.",
    ["This is a sentence, e.g. for me"]),
   # 4
   ("E. g. this is a sentence.",
    ["E. g. this is a sentence"]),
   # 5
   ("An above average chance stands e.g. Michael. Marta is also on the list.",
    ["An above average chance stands e.g. Michael",
     "Marta is also on the list"]),
   # Add more entries here:
))
def test_sentencesegmenter(sentence, expected):
    """checks whether sentencesegmenter behaves sane"""
    sentences = sentencesegmenter(sentence)
    assert sentences == expected
