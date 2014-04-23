#!/usr/bin/python3

from __future__ import print_function
import sys
import os
import re

# FIXME: this information should come from the script itself...
__programname__ = "SUSE Documentation Style Checker"
__version__ = "0.1.0pre"
__author__ = "Stefan Knorr"
__license__ = "MIT"
__description__ = "checks a given DocBook XML file for stylistic errors"

try:
    from distutils.core import setup
except ImportError:
    print("No distutils module found.", file=sys.stderr)
    sys.exit(10)


def listdir(path, ignore=None):
    """Lists all files recursively, starting from a given directory
    """
    all = []
    for root, sub, files in os.walk(path):
        for f in files:
            all.append(os.path.join(root, f))

    if ignore:
        all = [i for i in all for j in ignore if not re.search(j, i)]

    return all

print("All files: %s" % listdir("specs"))

setup(name='suse-doc-style-checker',
      version=__version__,
      description=__description__,
      long_description="suse-doc-style-checker ",
      author=__author__,
      author_email='sknorr@suse.de',
      url='git@gitorious.org:style-checker/style-checker.git',
      download_url='git@gitorious.org:style-checker/style-checker.git',
      license=__license__,
      data_files=[('.',                  ['LICENSE', ]),
                  ('source/',            listdir('source/')),
                  ('bookmarklet/',       listdir('bookmarklet')),
                  ('man/',               listdir('man')),
                 ],
      )

# EOF
