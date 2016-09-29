#

from lxml import etree
import pytest
import re
import sdsc


def test_terminologydtd(terminologyxml, terminologydtd):
    """FIXME@sknorr"""
    doc = etree.parse(terminologyxml)
    if not terminologydtd.validate(doc):
        raise AssertionError(terminologydtd.error_log.filter_from_errors()[0])
