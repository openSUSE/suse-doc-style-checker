#

import pytest
import os
import sdsc


def test_check_performance(capsys, casesdir):
    """checks whether the flag_performance stuff works"""
    sdsc.flag_performance = True
    path = "{}a-an.xml".format(casesdir)
    sdsc.checkOneFile(path)
    assert capsys.readouterr()[0].count("Running module") > 0
    sdsc.flag_performance = False


def test_main(capsys):
    """runs __main__.py"""
    with pytest.raises(SystemExit):
        path = os.path.dirname(os.path.realpath(__file__)) + "/../src/sdsc/__main__.py"
        exec(compile(open(path).read(), path, "exec"), {}, {"__name__": "__main__"})


def test_sdsc_version(capsys):
    """checks for output of sdsc --version"""
    assert sdsc.main(["--version"]) == 0
    out, _ = capsys.readouterr()
    assert sdsc.__version__ == out.split()[-1]


def test_sdsc_output(capsys, casesdir):
    """checks whether output to files works"""
    path = "{}a-an.xml".format(casesdir)
    sdsc.main([path, "/dev/null"])
    out, _ = capsys.readouterr()
    assert out == "/dev/null\n"
