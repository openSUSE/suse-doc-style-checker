#!/usr/bin/python3

from __future__ import print_function
import sys
import os
import re

sys.path.append("source")

import docstylecheck

try:
    from distutils.core import setup
except ImportError:
    print("No distutils module found.", file=sys.stderr)
    #from setuptools import setup
    sys.exit(10)


def listdir(path, ignore=None):
    """Lists all files recursively, starting from a given directory
    """
    all=[]
    for root, sub, files in os.walk(path):
        for f in files:
           all.append( os.path.join(root, f) )

    if ignore:
        all = [ i for i in all for j in ignore if not re.search(j, i) ]

    return all

print("All files: %s" % listdir("specs") )

setup(  name = 'docstylecheck',
  version = docstylecheck.__version__,
  description = docstylecheck.__description__,
  long_description="",
  author = docstylecheck.__author__,
  author_email = 'sknorr@suse.de',
  url = 'git@gitorious.org:style-checker/style-checker.git',
  download_url = 'git@gitorious.org:style-checker/style-checker.git' ,
  license = docstylecheck.__license__,
  # keywords = '',
  # classifiers=[],
  # install_requires=["lxml"],
  scripts=["source/docstylecheck.py"],
  data_files = [('.',     ['LICENSE', 'README.md'] ),
                ('source/xsl-checks/', listdir('source/xsl-checks/') ),
                ('specs', listdir("specs", (".tmp", ".profiled")) ),
               ],
  # package_data={ 'specs': ['specs']},
)

# EOF
