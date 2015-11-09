#
#
import pytest

from sdsc import __version__
from sdsc.__main__ import main

def test_version():
    """checks for the version"""
    assert __version__

def test_main():
    with pytest.raises(SystemExit):
        main([])
