#
# Copyright (c) 2015-2016 SUSE Linux GmbH
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

import sys


def printcolor(message, messagetype=None):
    """Print a colored message

    :param str message: Message
    :param str messagetype: Type (none => green, 'error' => red, 'debug' => blue)
    """
    if sys.stdout.isatty():
        if messagetype == 'error':
            print('\033[0;31m' + message + '\033[0m', file=sys.stderr)
        elif messagetype == 'debug':
            print('\033[0;36m' + message + '\033[0m', file=sys.stderr)
        else:
            print('\033[0;32m' + message + '\033[0m', file=sys.stdout)
    elif messagetype == 'error' or messagetype == 'debug':
        print(message, file=sys.stderr)
    else:
        print(message)
