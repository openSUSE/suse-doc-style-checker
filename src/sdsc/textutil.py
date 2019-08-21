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
from .const import (
        ENDPUNCTUATION,
        STARTPUNCTUATION,
        SENTENCEENDS,
        LASTSENTENCEENDS,
                   )


def removepunctuation(word, start=False, end=False):
    """Removes punctuation from beginning/end of tokens (i.e. does not
    expect sentences!).

    :param str text: token that we want to look at
    :param bool start: remove punctuation from start of token?
    :param bool end: remove punctuation from end of token?
    :return: word without quotes
    :rtype: str
    """

    if isinstance(word, list):
        if start:
            word = [removepunctuation(word[0], start=True)] + word[1:]
        if end:
            word = word[:-1] + [removepunctuation(word[-1], end=True)]
        return word

    if start:
        word = word.lstrip(STARTPUNCTUATION)
    if end:
        word = word.rstrip(ENDPUNCTUATION)
    return word


def sanitizepunctuation(text, quotes=False, apostrophes=False):
    """Ensures that we always work on the same kind of quotes and apostrophes.

    :param str text: text that we want to look at
    :param bool quotes: should quotes be sanitized?
    :param bool apos: should apostrophes be sanitized?
    :return: quoted text
    :rtype: str
    """

    if quotes:
        # FIXME: In enough cases, using this will lose the information whether this
        # was a opening quote or a closing quote.
        # Replace quotes only if they are at start/end of a word.

        quote = re_compile(r'((?<=^)[«»‹›“”„‟‘’‚‛「」『』](?=[\w\d])|'
                           r'(?<=\s)[«»‹›“”„‟‘’‚‛「」『』](?=[a-z0-9])|'
                           r'(?<=[\w\d])[«»‹›“”„‟‘’‚‛「」『』](?=$|[^\w\d]))',
                           re.I)
        # I need the quote_before version additionally because look-behinds must
        # be fixed-length -- it is expensive to try to be correct. Bah.
        quote_before = re_compile(r'((?<=[^\w\d])[«»‹›“”„‟‘’‚‛「」『』](?=[\w\d])|'
                                  r'(?<=\s)[«»‹›“”„‟‘’‚‛「」『』](?=[a-z0-9]))',
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
    # FIXME: For non-XML content, we need to split at /, however, in
    #content-pretty, we might destroy XML tags doing that. Ugh!
    # FIXME: We also currently cut away '—', again, that is (mostly) fine for
    # normal content but it is not for pretty content.
    #return text.split(' \n\r\t\v—/\\')
    # replace "client/server" with "client / server", but avoid breaking up
    # "server</quote>"
    # FIXME: Paths like /usr/bin/foo are split up as /usr / bin / foo
    text = re.sub(r'([\w\d])([—/])([\w\d])', r'\1 \2 \3', text)
    return text.split()


def sentencesegmenter(text):
    """Splits a paragraph into a list of sentences. Removes
    final punctuation from all sentences.

    :param str text: text to split into sentences
    """
    sentences = SENTENCEENDS.split(text)
    # The last sentence's final punctuation has not yet been cut off, do that
    # now.
    sentences[-1] = LASTSENTENCEENDS.sub('', sentences[-1])

    # We also need to cut off parentheses etc. from the first word of the first
    # sentence, as that has not been done so far either.
    sentences[0] = removepunctuation(sentences[0], start=True)
    return sentences
