#

import pytest

#True
#        tagtype = str(tagsreplaced.group(1))
#        tokens = int(tagsreplaced.group(2))
from sdsc.tokens import findtagreplacement


@pytest.mark.parametrize("text,result",
  (
    # 0 - normal text, no op
    ('noop',(False, None, 1)),
    # 1 - regular tag replacement
    ('##@cooltag-1##',(True, 'cooltag', 1)),
    # 2 - regular tag replacement
    ('##@cooltag-2##',(True, 'cooltag', 2)),
    # 3 - tricky case that should never happen since the text should always be
    #     a single token only -- still, we should find something in there
    ('Michael Caine approves of this ##@cooltag-1##',(True, 'cooltag', 1)),
    # 4 - tricky case with a dash in the replaced tag -- should not happen and
    # we should not find anything in there
    ('##@cool-tag-1##',(False, None, 1)),
    # 5 - replacement for a tag like <cooltag>  </cooltag> (i.e. no content)
    #     this behavior is ... controversial: also see
    #     tests/cases/sentencelength.xml +29
    ('##@cooltag-0##',(True, 'cooltag', 0)),
  )
)
def test_findtagreplacement(text,result):
    """checks whether placeholders for special tags are found"""
    assert findtagreplacement(text) == result
