#!/usr/bin/python

try:
    from distutils.core import setup
except ImportError, excp:
    from setuptools import setup

setup(  name = '',
  # version = pydot.__version__,
  description = '',
  long_description="",
  author = 'Stefan Knorr',
  author_email = 'sknorr@suse.de',
  url = '',
  download_url = '' ,
  license = 'MIT',
  keywords = 'graphviz dot graphs visualization',
  classifiers=[],
  data_files = [('.', ['LICENSE', 'README'])]
)

# EOF
