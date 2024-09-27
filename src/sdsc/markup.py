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

from .textutil import (
        tokenizer,
                      )

def highlight(tokens, highlightstart, highlightend):
    """Takes a string and adds XML tags that lead to specified
    tokens being highlighted in the output file.

    :param tokens: list of words or a string:
        ["highlight", "these", "two", "words"] or
        "highlight these two words" (will be tokenized automatically)
    :param int highlightstart: start highlighting before this token (starting from zero)
    :param int highlightend: stop highlighting after this token (starting from zero)
    :return: string with <highlight> tags at appropriate places"""

    tokens = tokens[:]
    if isinstance(tokens, str):
        return highlight(tokenizer(tokens), highlightstart, highlightend)

    highlightstart = max(highlightstart, 0)
    highlightend = max(highlightend, 0)
    highlightend = min(highlightend, len(tokens) - 1)

    if highlightstart >= len(tokens) or highlightend < highlightstart:
        return ""  # Nothing to highlight


    tokens[highlightstart] = "<highlight>" + tokens[highlightstart]
    tokens[highlightend] = tokens[highlightend] + "</highlight>"

    return " ".join(tokens)
