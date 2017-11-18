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


# In manglepattern(), only catch patterns that are not literal and are not
# followed by an indicator of a lookahead/lookbehind (?) or are already
# non-capturing groups
# FIXME: This will fail on character classes like: [(]
PARENTHESES = re.compile(r'(?<!\\)\((?![\?|\:])')


# Sentence end characters.
# FIXME: English hardcoded
# Lookbehinds need to have a fixed length... thus .ca
# Do not use capture groups together with re.split, as it does additional splits
# for each capture group it finds.
SENTENCEENDS = re.compile(r'(?<![Ee]\.g|etc|[Ii]\.e|.ca|[Nn]\.[Bb]|[Ii]nc)'
                          '(?:\.?\.?[.!?]|[:;])\s+[[({]?'
                          '(?=(?:[A-Z0-9#]|openSUSE))')
LASTSENTENCEENDS = re.compile(r'(?<![Ee]\.g|etc|[Ii]\.e|.ca|[Nn]\.[Bb]|[Ii]nc)'
                              '(?:\.?\.?[.!?][])}]?|[:;])\s*$')


# trypatterns() checks if a sub-pattern of a given pattern matches nothing
# (and looks unusual while doing that), i.e. subpatterns like (this|), (|this),
# or (th||is)
# FIXME: This will fail on character classes like: [(|]
EMPTYSUBPATTERN = re.compile(r'(?<!\\)(\|\)|\(\||\|\|)')


STARTPUNCTUATION = '([{"\'¡¿<“„‟‘‚‛「『【〚〖〘〔〈《'
ENDPUNCTUATION = '〉》〕〙〗〛】”’‛」』>)]}/\\"\',:;!?.‥…‼‽⁇⁈⁉'

# Filters for the spell checker
# SPELLFILTER -- Used to kick out bare-text file names etc.
# SPELLPUNCTATION -- To remove any punctuation that is still at the beginning
#  or end of the word (and also `'s` possessive endings).

# FIXME: Our use case is hardcoded
SPELLFILTER = re.compile('(([a-z]{3,6}#?)[0-9]+|[-—.?<>/\\|\'"{}~`!@#$%^&*()\[\]_=+]+|[a-z]+://.*|[a-z]+\.(log|conf(ig)?|ini|h(xx)?|c(xx)?|o|ldif|diff|xml|xsl|html?|pl|do[ct]x?|xl[st]x?|pp[st]x?|odt|ods|odg|odp))', re.I)
SPELLSIMPLIFIER = re.compile('(^[^-_.\d\w]+|(\'s|[®*!?.:;^])+$)')
SPELLWORDSEPARATORS = re.compile('[-–—+/\\]')
