import os
import sys
import re
import pytest
from lxml import etree
import sdsc


def test_main(capsys):
    """runs __main__.py"""
    with pytest.raises(SystemExit):
        path = os.path.dirname(os.path.realpath(__file__)) + "/../src/sdsc/__main__.py"
        exec(compile(open(path).read(), path, "exec"), {}, {"__name__": "__main__"})


def test_check_performance(capsys):
    """checks whether the flag_performance stuff works"""
    sdsc.flag_performance = True
    path = os.path.dirname(os.path.realpath(__file__)) + "/cases/a-an.xml"
    sdsc.checkOneFile(path)
    assert  capsys.readouterr()[0].count("Running module") > 0
    sdsc.flag_performance = False


def test_sdsc_output(capsys):
    """checks whether output to files works"""
    path = os.path.dirname(os.path.realpath(__file__)) + "/cases/a-an.xml"
    sdsc.main([path, "/dev/null"])
    out, _ = capsys.readouterr()
    assert out == "/dev/null\n"


def test_sdsc_version(capsys):
    """checks for output of sdsc --version"""
    assert sdsc.main(["--version"]) == 0
    out, _ = capsys.readouterr()
    assert sdsc.__version__ == out.split()[-1]


def test_tokenizer():
    """checks whether the tokenizer works as expected"""
    tokens = sdsc.tokenizer("This is a simple sentence.")
    assert tokens == ["This", "is", "a", "simple", "sentence."]
    tokens = sdsc.tokenizer("This is a less simple sentence with a\xa0nbsp.")
    assert tokens == ["This", "is", "a", "less",
                      "simple", "sentence", "with", "a", "nbsp."]


def test_sentencesegmenter():
    """checks whether sentencesegmenter behaves sane"""
    sentences = sdsc.sentencesegmenter("This is a simple ##@command-2## sentence. This one too.")
    assert sentences == ["This is a simple ##@command-2## sentence", "This one too"]
    sentences = sdsc.sentencesegmenter(
        "This is not a test in one go. openSUSE is not written with a capital letter.")
    assert sentences == ["This is not a test in one go",
                         "openSUSE is not written with a capital letter"]
    sentences = sdsc.sentencesegmenter("This is a sentence, e.g. for me.")
    assert sentences == ["This is a sentence, e.g. for me"]
    sentences = sdsc.sentencesegmenter("E. g. this is a sentence.")
    assert sentences == ["E. g. this is a sentence"]
    sentences = sdsc.sentencesegmenter(
        "An above average chance stands e.g. Michael. Marta is also on the list.")
    assert sentences == ["An above average chance stands e.g. Michael",
                         "Marta is also on the list"]


def test_isDupe():
    """checks whether isDupe is correct"""
    tokens = ["this", "is", "a", "test"]
    assert sdsc.isDupe(tokens, 2) == 0
    tokens = ["this", "is", "is", "a", "test"]
    assert sdsc.isDupe(tokens, 2) == 1
    tokens = ["this", "is", "this", "is", "a", "test"]
    assert sdsc.isDupe(tokens, 2) == 2
    tokens = ["this", "is", "(this", "is)", "a", "test"]
    assert sdsc.isDupe(tokens, 2) == 0


def test_highlighter():
    """checks whether the highlight function works"""
    xml = sdsc.highlight(["highlight", "these", "two", "words"], 1, 2)
    assert xml == "highlight <highlight>these two</highlight> words"


def test_contextpatternlocations():
    """checks the contextpatternlocations function"""
    assert sdsc.contextpatternlocations([1], [1]) == [1]
    assert sdsc.contextpatternlocations([2], [-1, 1]) == [-2, 2]
    assert sdsc.contextpatternlocations([3], [1], True) == [1, 2, 3]
    assert sdsc.contextpatternlocations([3], [-1], True) == [-1, -2, -3]


def test_xml(xmltestcase):
    """Runs specified testcase and validates the output of all checks.
    The xmltestcase fixture returns all files in tests/cases"""
    nr_errors = 0

    testname = os.path.basename(xmltestcase)
    try:
        resultxml = sdsc.checkOneFile(xmltestcase)
    except etree.Error as error:
        pytest.fail("Syntax error in testcase {0!r}: {1}!".format(testname, error.msg))

    # Parse the input file and gather all ids
    inputtree = etree.parse(xmltestcase)
    inputids = []
    for elem in inputtree.getiterator():
        eid = elem.get("{http://www.w3.org/XML/1998/namespace}id", elem.get("id")) 
        if eid is not None:
            if eid.count("sdsc."):
                if eid in inputids:
                    pytest.fail(
                        "Duplicate ID {0!r} in case {1!r}!".format(eid, testname))

                inputids.append(eid)
    if len(inputids) == 0:
        pytest.skip("No tests found in {0}".format(testname))

    # Parse the result file and collect ids of errors and warnings
    resulttree = etree.fromstring(resultxml)
    complaints = {}
    currentPartSource = ""
    for elem in resulttree.getiterator():
        if elem.tag == "part":
            currentPartSource = elem.get("source")
            complaints[currentPartSource] = []
        elif elem.tag == "result":
            elemType = elem.get("type", "info")
            if elemType == "info":
                # Not interested in those. They don't have an ID either...
                continue

            withinid = elem.findtext("location/withinid")
            message = elem.find("message")
            if withinid is None:
                withinid = elem.findtext("message/id")
                if withinid is None:
                    pytest.fail("No withinid found")

            formattedMessage = "<no message>"
            if message is not None:
                formattedMessage = etree.tostring(
                    message, method="text", encoding='UTF-8').decode(encoding='UTF-8')
                # Remove excessive whitespace and newlines
                formattedMessage = " ".join(formattedMessage.split()).strip()

            complaints[currentPartSource].append(
                {'id': withinid, 'message': formattedMessage, 'type': elemType})

    # Isolate unexpected warnings
    for checkmodule, complaintList in complaints.items():
        for complaint in complaintList:
            if not complaint["id"].count("sdsc.expect.{0}.{1}".format(complaint["type"], checkmodule)):
                print("Unexpected {0} {1!r} generated by module {2!r} for ID {3!r}.".format(complaint[
                    "type"], complaint["message"], checkmodule, complaint["id"]), file=sys.stderr)
                nr_errors += 1

    # Now check for missing errors and warnings
    for eid in inputids:
        # Regex for test_sdsc special ids ("stuff.sdsc.expect.warning.a-an.1")
        findExpect = re.search(r'.*sdsc\.expect\.([^.]+)\.([^.]+)(?:\..*|$)', eid)
        if not findExpect:
            continue
        found = False
        if findExpect.group(2) in complaints:
            found = sum(complaint["id"] == eid and complaint["type"] == findExpect.group(
                1) for complaint in complaints[findExpect.group(2)])

        if not found:
            print("Expected {0} for ID {1!r} generated by module {2!r}.".format(
                findExpect.group(1), eid, findExpect.group(2)), file=sys.stderr)
            nr_errors += 1

    if nr_errors > 0:
        pytest.fail(msg="Test {0!r} failed with {1} errors!".format(
            os.path.basename(xmltestcase), nr_errors), pytrace=False)
