#!/usr/bin/env python3

#
# Copyright (c) 2015 SUSE Linux GmbH
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#

"""SDSC Module that handles CLI-related tasks
"""

from . import __description__, __programname__, __version__

import argparse
import sys

# TODO: Get rid of the entire "positional arguments" thing that argparse adds
# (self-explanatory anyway). Get rid of "optional arguments" header. Make sure
# least important options (--help, --version) are listed last. Also, I really
# liked being able to use sentences in the parameter descriptions.

def parseargs(cliargs=None):
    """Parse command line arguments

    :param list cliargs: Arguments to parse or None (=use sys.argv)
    :return: parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        usage = "%(prog)s [options] inputfile [outputfile]",
        description = __description__ )
    fileorbookmark = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('-v', '--version',
        action = 'version',
        version = __programname__ + " " + __version__,
        help = "show version number and exit")
    fileorbookmark.add_argument( '-b', '--bookmarklet',
        action = 'store_true',
        default = False,
        help = """open Web page that lets you install a bookmarklet to manage
            style checker results""" )
    parser.add_argument( '-s', '--show',
        action = 'store_true',
        default = False,
        help = """show final report in $BROWSER, or default browser if unset; not
            all browsers open report files correctly and for some users, a text
            editor will open; in such cases, set the BROWSER variable with:
            export BROWSER=/MY/BROWSER ; Chromium or Firefox will both
            do the right thing""" )
    parser.add_argument( '--module',
        action = 'store_true',
        default = False,
        help = "writes name of current check module to stdout" )
    parser.add_argument( '--performance',
        action = 'store_true',
        default = False,
        help = "write performance measurements to stdout" )
    parser.add_argument( '--checkpatterns',
        action = 'store_true',
        default = False,
        help = """check formal validity of built-in regular expression
            patterns""" )
    fileorbookmark.add_argument( 'inputfile', type=argparse.FileType('r'),
        nargs = "?" )
    parser.add_argument( 'outputfile', nargs = "?" )

    return parser.parse_args(args=cliargs)


def printcolor( message, messagetype = None ):
    """Print a colored message

    :param str message: Message
    :param str messagetype: Type (none => green, 'error' => red)
    """
    if sys.stdout.isatty():
        if type == 'error':
            print( '\033[0;31m' + message + '\033[0m' )
        else:
            print( '\033[0;32m' + message + '\033[0m' )
    else:
        print( message )
