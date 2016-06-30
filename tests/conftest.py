import glob
import os
import sdsc
import pytest
from lxml import etree

@pytest.fixture(scope="session", autouse=True)
def initialize_sdsc():
    sdsc.initialize()

def pytest_generate_tests(metafunc):
    """Replace the xmltestcases fixture by all files in tests/cases """
    if 'xmltestcase' in metafunc.fixturenames:
        location = os.path.dirname(os.path.realpath(__file__))
        testcases = glob.glob(location + "/cases/*")
        testcases.sort() # Sort them alphabetically
        metafunc.parametrize("xmltestcase", testcases)
    elif 'terminologyvalidation' in metafunc.fixturenames:
        location = os.path.join(os.path.dirname(__file__), '../src/sdsc/xsl-checks')
        testcase = glob.glob(location + "/*.xml")
        metafunc.parametrize("terminologyvalidation", testcase)

@pytest.fixture(scope="session")
def terminologydtd():
    dtdfile = os.path.join(os.path.dirname(__file__), '../validation/terminology.dtd')
    dtd = etree.DTD(file=dtdfile)
    return dtd

