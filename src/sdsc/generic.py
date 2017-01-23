#
# Copyright (c) 2017 SUSE Linux GmbH
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

import re

RE_CACHE = {}

def re_compile(pattern, flags=0):
    """re.compile caches only a small number of regular expressions. Our
    version can cache a much larger number of them which increases speed
    since expressions do not have to be recompiled all the time.
    """

    try:
        return RE_CACHE[flags][pattern]
    except KeyError:
        if flags not in RE_CACHE:
            RE_CACHE[flags] = {}
        RE_CACHE[flags][pattern] = re.compile(pattern, flags)

        return RE_CACHE[flags][pattern]


def linenumber(context):
    """ Find out line number from the source document. This is currently buggy
    for two reasons:
    1. libxml uses the wrong data type to provide this number which means that
       we only get to around 65000 lines or so, which is often too little.
    2. Line numbers in the profiled XML bigfile have little to do with the
       original line numbers.
    Nevertheless, this line number is added to the output but later hidden
    via CSS.
    """

    return context.context_node.sourceline
