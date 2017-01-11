#

import pytest
import sdsc

@pytest.mark.parametrize("params,result",
  (
    # 0 - just quotes, no op
    (('Absence makes the heart grow fonda, “Jane”', False, False),'Absence makes the heart grow fonda, “Jane”'),
    # 1 - just quotes
    (('Absence makes the heart grow fonda, “Jane”', True, True),'Absence makes the heart grow fonda, "Jane"'),
    # 2 - trickier case with punctuation after the second quote
    (('«I don’t believe you know what you are doing», he said.', True, True),'"I don\'t believe you know what you are doing", he said.'),
    # 3 - same case but apostrophe replacement only
    (('«I don’t believe you know what you are doing», he said.', False, True),'«I don\'t believe you know what you are doing», he said.'),
    # 4 - same case but quote replacement only
    (('«I don’t believe you know what you are doing», he said.', True, False),'"I don’t believe you know what you are doing", he said.'),
    # 5 - Quotes in the middle of the sentence
    (('I don’t believe 『you』 know what you are doing. Subtlety isn`t your forté, is it?', True, True),'I don\'t believe "you" know what you are doing. Subtlety isn\'t your forté, is it?'),
  )
)
def test_sanitizepunctuation(params,result):
    """checks whether punctuation is properly sanitized (i.e. whether quotes and apostrophes are removed properly)"""
    assert sdsc.sanitizepunctuation(*params) == result
