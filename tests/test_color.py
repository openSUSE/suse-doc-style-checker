#

import pytest
import re
from sdsc import printcolor


@pytest.mark.parametrize("msg",  ("hello",)
)
@pytest.mark.parametrize("msgtype",
                         ("error", "debug", None)
)
@pytest.mark.parametrize('isatty', (True, False))
def test_printcolor(capsys, monkeypatch, msg, msgtype, isatty):
    """Checks printcolor() function

    :param capsys:
    :param str msg:
    :param str msgtype:
    :param bool isatty:
    """
    monkeypatch.setattr('sys.stdout.isatty', lambda: isatty)

    printcolor(msg, msgtype)
    if msgtype in ('debug', 'error'):
        assert capsys.readouterr()[0].count(msg) == 0
    else:
        assert capsys.readouterr()[0].count(msg) > 0

