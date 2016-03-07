import pytest

import sdsc

def test_main():
    with pytest.raises(SystemExit):
        sdsc.main([])

def test_sdsc_version(capsys):
    """checks for output of sdsc --version"""
    with pytest.raises(SystemExit):
        sdsc.main(["--version"])
    out, err = capsys.readouterr()
    assert sdsc.__version__ == out.split()[-1]
