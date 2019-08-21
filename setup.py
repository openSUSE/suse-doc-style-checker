#!/usr/bin/env python3

import io
import os
import os.path
import re

from setuptools import setup, find_packages

# FIXME: this information should come from the script itself...
__projectname__ = "suse-doc-style-checker"
__programname__ = "SUSE Documentation Style Checker"
# __version__ will be read from sdsc/__init__.py
__authors__ = "Stefan Knorr, Thomas Schraitle"
__license__ = "LGPL-2.1+"
__description__ = "checks a given DocBook XML file for stylistic errors"

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*names, **kwargs):
    """Read in file
    """
    with io.open(os.path.join(HERE, *names),
                 encoding=kwargs.get("encoding", "utf8")) as fp:
        return fp.read()


def find_version(*file_paths):
    """Read __version__ string from file paths

    :return: version string
    :rtype: str
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setupdict = dict(
    name=__projectname__,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://python-packaging-user-guide.readthedocs.org/en/latest/single_source_version/
    version=find_version("src", "sdsc", "__init__.py"),  # __version__,

    description=__description__,
    long_description="Checks a given DocBook XML file for stylistic errors using check files written in XSLT",

    # The project's main homepage.
    url='https://www.github.org/openSUSE/suse-doc-style-checker',
    download_url='https://github.org/openSUSE/suse-doc-style-checker/releases',

    # Author details
    author=__authors__,
    author_email='sknorr@suse.de',

    license=__license__,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',

        # Supported Python versions
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords=["docbook5", "style", "style-checking"],

    # ----
    # Includes data files from MANIFEST.in
    #
    # See also:
    # http://stackoverflow.com/a/16576850
    # https://pythonhosted.org/setuptools/setuptools.html#including-data-files
    include_package_data=True,

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # toms: Check this
    packages=find_packages('src', exclude=('.+\.xml',)),
    package_dir={'': 'src'},

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['lxml'],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #    '':              ['LICENSE' ],
    #    },

    # toms: data_files is not needed anymore as it is all handled by MANIFEST.in
    # data_files =  [('.',                 ['LICENSE', ]),
    #  #...
    #                ],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': ['sdsc=sdsc:main'],
    },

    # Required packages for using "setup.py test"
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'pytest-catchlog'],

    # Actually run tests
    # cmdclass = {'test': PyTest},
)


# Call it:
setup(**setupdict)

# EOF
