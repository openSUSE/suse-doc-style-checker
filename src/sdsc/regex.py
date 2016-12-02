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

import re

__all__ = ['parentheses', 'sentenceends', 'lastsentenceends',
           'emptysubpattern', 're_compile']


# In manglepattern(), only catch patterns that are not literal and are not
# followed by an indicator of a lookahead/lookbehind (?) or are already
# non-capturing groups
# FIXME: This will fail on character classes like: [(]
parentheses = re.compile(r'(?<!\\)\((?![\?|\:])')

# Sentence end characters.
# FIXME: English hardcoded
# Lookbehinds need to have a fixed length... thus .ca
# Do not use capture groups together with re.split, as it does additional splits
# for each capture group it finds.
sentenceends = re.compile(r'(?<![Ee]\.g|etc|[Ii]\.e|.ca|[Nn]\.[Bb]|[Ii]nc)(?:\.?\.?[.!?]|[:;])\s+[[({]?(?=(?:[A-Z0-9#]|openSUSE))')
lastsentenceends = re.compile(r'(?<![Ee]\.g|etc|[Ii]\.e|.ca|[Nn]\.[Bb]|[Ii]nc)(?:\.?\.?[.!?][])}]?|[:;])\s*$')

# trypatterns() checks if a sub-pattern of a given pattern matches nothing
# (and looks unusual while doing that), i.e. subpatterns like (this|), (|this),
# or (th||is)
# FIXME: This will fail on character classes like: [(]
emptysubpattern = re.compile(r'(?<!\\)(\|\)|\(\||\|\|)')

# FIXME: ???
re_cache = {}


def re_compile(pattern, flags=0):
    """Caching version of re.compile"""
    try:
        return re_cache[flags][pattern]
    except KeyError:
        if flags not in re_cache:
            re_cache[flags] = {}
        re_cache[flags][pattern] = re.compile(pattern, flags)

        return re_cache[flags][pattern]
