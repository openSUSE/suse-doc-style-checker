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
from .generic import re_compile


def removepunctuation(word, start=False, end=False):
    """Removes punctuation from beginning/end of tokens (i.e. does not
    expect sentences!).

    Parameters:
    text  - str(), token that we want to look at
    start  - bool(): remove punctuation from start of token?
    apos   - bool(): remove punctuation from end of token?
    """

    if isinstance(word, list):
        if start:
            word = [removepunctuation(word[0], start=True)] + word[1:]
        if end:
            word = word[:-1] + [removepunctuation(word[-1], end=True)]
        return word

    startpunctuation = '([{"\'¡¿<“„‟‘‚‛「『【〚〖〘〔〈《'
    endpunctuation = '〉》〕〙〗〛】”’‛」』>)]}/\\"\',:;!?.‥…‼‽⁇⁈⁉'

    if start:
        word = word.lstrip(startpunctuation)
    if end:
        word = word.rstrip(endpunctuation)
    return word


def sanitizepunctuation(text, quotes=False, apostrophes=False):
    """Ensures that we always work on the same kind of quotes and apostrophes.

    :param str text: text that we want to look at
    :param bool quotes: quotes should quotes be sanitized?
    :param bool apos: quotes should apostrophes be sanitized?
    :return: quoted text
    :rtype: str
    """

    if quotes:
        # FIXME: In enough cases, using this will lose the information whether this
        # was a opening quote or a closing quote.
        # Replace quotes only if they are at start/end of a word.

        quote = re_compile(r'((?<=^)[«»‹›“”„‟‘’‚‛「」『』]'
                           r'(?=[\w\d])|'
                           r'(?<=\s)[«»‹›“”„‟‘’‚‛「」『』]'
                           r'(?=[a-z0-9])|'
                           r'(?<=[\w\d])[«»‹›“”„‟‘’‚‛「」『』]'
                           r'(?=$|[^\w\d]))',
                           re.I)
        # I need the quote_before version additionally because look-behinds must
        # be fixed-length -- it is expensive to try to be correct. Bah.
        quote_before = re_compile(r'((?<=[^\w\d])[«»‹›“”„‟‘’‚‛「」『』]'
                                  r'(?=[\w\d])|'
                                  r'(?<=\s)[«»‹›“”„‟‘’‚‛「」『』]'
                                  r'(?=[a-z0-9]))',
                                  re.I)
        text = quote.sub('"', text)
        text = quote_before.sub('"', text)
    if apostrophes:
        apostrophe = re_compile(r'[’՚\'ʼ＇｀̀́`´ʻʹʽ]')
        text = apostrophe.sub('\'', text)
    return text


def findtagreplacement(text):
    """Search through a token to see whether it contains a replaced tag.
    Allows finding a single tag replacement only.

    text - str(): a token
    """

    tagfound = False
    tagtype = None
    tokens = 1

    tagreplacement = re_compile(r'##@(\w+)-(\d+)##')
    tagsreplaced = tagreplacement.search(text)

    if tagsreplaced:
        tagfound = True
        tagtype = str(tagsreplaced.group(1))
        tokens = int(tagsreplaced.group(2))

    return (tagfound, tagtype, tokens)


def counttokens(context, text):
    """Counts the number of tokens in a given string. This
    is used to enable tag replacement for content that needs
    to be skipped and conversely to re-insert skipped text and
    enable highlighting.

    :param str context: context node (ignored)
    :param str text: text in which to count tokens
    """
    del context  # not used
    count = 0
    if text:
        count = len(tokenizer(text[0]))
    return count


def xmlescape(text):
    """Escapes XML input to enable working with it.

    :param str text: string to be escaped
    :return: escaped string
     """
    escapetable = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
        }
    return "".join(escapetable.get(c, c) for c in text)


def tokenizer(text):
    """Splits a string into a list of words.

    :param str text: text to split into tokens
    """
    return text.split()
