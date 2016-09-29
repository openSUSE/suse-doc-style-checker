#

import pytest
import re
from sdsc import printcolor


@pytest.mark.parametrize("msg",
                         ("a", "b\nc")
)
@pytest.mark.parametrize("msgtype",
                         ("error", "debug", None)
)
# @pytest.mark.parametrize('isatty', (True, False))
def test_printcolor(capsys, msg, msgtype):
    """Checks printcolor() function

    :param str msg:
    :param str msgtype:
    :param capsys:
    """
    printcolor(msg, msgtype)
    if msgtype in ('debug', 'error'):
        assert capsys.readouterr()[0].count(msg) == 0
    else:
        assert capsys.readouterr()[0].count(msg) > 0

