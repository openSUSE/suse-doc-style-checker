#

from lxml import etree
import pytest
import re
import sdsc


def test_terminologydtd(terminologyxml, terminologydtd):
    """Checks whether the XML files included with the XSLT check
       files validate against the terminology DTD
       ([repo]/validation/terminology.dtd)

    :param str terminologyxml: Fixture which points to XML file
    :param str terminologydtd: Fixture which points to the terminology.dtd file
    """
    doc = etree.parse(terminologyxml)
    if not terminologydtd.validate(doc):
        raise AssertionError(terminologydtd.error_log.filter_from_errors()[0])
