#

import pytest
import sdsc


def test_checkpatterns(capsys, casesdir):
    """checks whether the patterns are sane"""
    sdsc.flag_checkpatterns = True
    path = "{}aan.xml".format(casesdir)
    sdsc.checkOneFile(path)
    sdsc.flag_checkpatterns = False


@pytest.mark.parametrize("params,result",
 (
   # 1
   (([1], [1]),        [1]),
   # 2
   (([2], [-1, 1]),    [-2, 2]),
   # 3
   (([3], [1], True),  [1, 2, 3]),
   # 4
   (([3], [-1], True), [-1, -2, -3]),
 )
)
def test_contextpatternlocations(params, result):
    """checks the contextpatternlocations function"""
    assert sdsc.contextpatternlocations(*params) == result

