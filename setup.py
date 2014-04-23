#!/usr/bin/python3

from __future__ import print_function
import sys
import os
import re

#sys.path.append("source")
# import sdsc
__version__="0.0.99"
__description__=""
__author__=""
__license__="MIT"


try:
    from distutils.core import setup
except ImportError:
    print("No distutils module found.", file=sys.stderr)
    #from setuptools import setup
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
      # keywords = '',
      # classifiers=[],
      # install_requires=["lxml"],
      # scripts=["source/sdsc"],
      data_files=[('.',                  ['LICENSE', ]),
                  ('source/',            listdir('source/')),
                  #('source/',            listdir('source/', ('validation', 'xsl-checks'))),
                  #('source/xsl-checks/', listdir('source/xsl-checks/')),
                  ('bookmarklet/',       listdir('bookmarklet')),
                  ('man/',               listdir('man')),
                 ],
      # package_data={ 'specs': ['specs']},
      )

# EOF
