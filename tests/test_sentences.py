#

import pytest
from sdsc import sentencesegmenter


@pytest.mark.parametrize("sentence,expected",
(
   # 0 - a single simple sentence
   ("This is a simple sentence.",
    ["This is a simple sentence"]),
   # 1 - two simple sentences
   ("This is a simple ##@command-2## sentence. This one is too.",
    ["This is a simple ##@command-2## sentence", "This one is too"]),
   # 2 - lowercase letter starts second sentence
   ("This is not a test in one go. openSUSE is not written with a capital letter.",
    ["This is not a test in one go",
     "openSUSE is not written with a capital letter"]),
   # 3 - abbreviation in the middle of the sentence
   ("This is a sentence, e.g. for me.",
    ["This is a sentence, e.g. for me"]),
   # 4 - abbreviation at the start of the sentence
   ("E. g. this is a sentence.",
    ["E. g. this is a sentence"]),
   # 5 - abbreviation in the middle of sentence before a capital letter
   ("An above average chance stands e.g. Michael. Marta is also on the list.",
    ["An above average chance stands e.g. Michael",
     "Marta is also on the list"]),
   # 6 - sentences with parentheses around them
   ("(We speak in circles. We dance in code.)",
    ["We speak in circles",
     "We dance in code"]),
   # 6 - sentences with parentheses around them
   ("We speak in circles. (We dance in code.)",
    ["We speak in circles",
     "We dance in code"]),
))
def test_sentencesegmenter(sentence, expected):
    """checks whether sentencesegmenter behaves sanely"""
    sentences = sentencesegmenter(sentence)
    assert sentences == expected
