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

from collections import namedtuple

#: new type
Accept = namedtuple('Accept', ['proposal', 'context'])

# list of accepted terms:
# accepts = [ [ 'proposal', 'context' ], [ 'proposal without context', None ], [ None, None ], ... ]
#             <accept/> #1,              <accept/> #2,                         <accept/> #3
# global accepts


class PatternGroup(object):
    """A group of nested patterns which belongs together

     A pattern group has a syntax of:

      [ [ pattern, pattern, pattern ], [ pattern, pattern ] ]
    """

    def __init__(self, *patterns):
        """ Prepare regular expression patterns contained in the <term/> elements
        of an XML source by extracting their main pattern and context patterns
        and appending the main pattern to onepattern (if use of onepattern is
        enabled)

        :param term: XML source of one <term/> element
        :type term: :class:`lxml.etree._ElementTree` | :class:`lxml.etree._Element`
        :param list onepattern: list of patterns
        :param bool useonepattern: use onepattern?
        """
        self._patterns = patterns

    def __repr__(self):
        return "<{}: {}>".format(type(self).__name__, len(self))

    def __len__(self):
        return len(self._patterns)

    def __iter__(self):
        yield from self._patterns

    def __getitem__(self, item):
        return self._patterns[item]


# list of contextpatterns, per patterngroup:
# patterns = [ [ [ contextpattern, [-2,-1], True ], [ contextpattern, [1], False ], ... ], [], ... ]
#              <patterngroup/> #1,                                                         <patterngroup/> #2
#                <contextpattern/> #1
#                                  position(s) of tokens to check relative to pattern1 [negative numbers => before]
#                                           matching mode [True => positive, pattern has to appear at least once]
#                                                   <contextpattern/> #2
#                                                                     position(s) of tokens to check relative to last [positive numbers => after]
#                                                                          matching mode [False => negative, pattern must not appear in any of given places]
# global contextpatterns
