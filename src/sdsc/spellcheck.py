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
import enchant
import os.path
from lxml import etree

from .const import SPELLFILTER
from .cli import printcolor
from .generic import (
        linenumber,
                     )
from .markup import (
        highlight,
                    )
from .textutil import (
        findtagreplacement,
        removepunctuation,
        sanitizepunctuation,
        sentencesegmenter,
        tokenizer,
        xmlescape,
                      )


def spellcheck(context, maindict, customdict, content, contentpretty,
               contextid, basefile, messagetype):
    """ Check a paragraph using using enchant's default spell checker. If there
    is a misspelling, issue a message.

    :param ??? context: information about the context node
    :param str maindict: system-wide main dictionary to use
    :param str customdict: extra word list to use (optional)
    :param str content: content, as formatted for the terminology check itself
    :param str contentpretty: content, as formatted for display in a message
    :param str contextid: next element with id attribute around the content
    :param str basefile: file in which content appears
    :param str messagetype: print a 'warning', 'info', or 'error' message?
    """

    # FIXME: Much of this is copypasta from termcheck(), though termcheck()
    # is much more complicated and a lot of conditions are removed in this
    # version. Refactor?

    if not content:
        return []

    # I get this as a list with one lxml.etree._ElementUnicodeResult.
    # I need a single string.
    # For whatever reason, this made spellcheckmessage() crash
    # happily and semi-randomly.
    content = sanitizepunctuation(str(content[0]), quotes=False, apostrophes=True)

    basefile = basefile[0] if basefile else None
    contextid = contextid[0] if contextid else None

    # sanitize this...
    if messagetype not in ('warning', 'info'):
        messagetype = 'error'

    # This if/else block should not be necessary (if there is content,
    # there should always also be pretty content, but that depends on the
    # XSLT used for checking). It hopefully won't hurt either.
    contentpretty = str(contentpretty[0]) if contentpretty else content

    # FIXME: profile this for speed -- we might have to make this global(ler).
    # Also, the approach o
    # need to convert byte string to string
    spelldict = 0
    if maindict and customdict:
        customdict = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'xsl-checks', str(customdict))
        spelldict = enchant.DictWithPWL(str(maindict), customdict)
    elif maindict:
        spelldict = enchant.Dict(str(maindict))
    else:
        printcolor('No dictionary for spellchecking selected.', 'error')

    sentences = sentencesegmenter(content)

    # the counter goes up for the first word already, i.e. token[0],
    # thus we just start at -1, so the first word gets to be 0.
    # FIXME: shorten to just currenttoken. the inparagraph part is obvi
    currenttokeninparagraph = -1

    messages = []
    for sentence in sentences:
        words = tokenizer(sentence)
        totalwords = len(words)

        skipcount = 0
        for wordposition, word in enumerate(words):
            # If we hit a placeholder, e.g. ##@key-1##, the number
            # (here: 1) signifies the number of tokens this placeholder
            # replaces. If no placeholder found, tagtokens is 1.
            istag, _, tagtokens = findtagreplacement(word)
            currenttokeninparagraph += tagtokens
            if istag:
                continue

            word = removepunctuation(word, start=True, end=True)

            # FIXME: English hardcoded
            # FIXME: store this
            word = re.sub('(^[^-_.\d\w]+|(\'s|[®*!?.:;^])+$)', '', word)

            # removepunctuation can lead to empty strings...
            if not word:
                continue
            # filter for numbers, punctuation, URLs, file names
            if SPELLFILTER.match(word):
                continue

            correct = spelldict.check(word)

            if not correct:
                # FIXME: can we order suggestions, e.g. for "ipc" (which is in
                # our dictionary as "IPC"), we only get irrelevant lower-case
                # suggestions and "IPC" removed later when we limit the choice
                # to 5 suggestions.
                suggestions = spelldict.suggest(word)

                line = linenumber(context)
                contenthighlighted = highlight(xmlescape(contentpretty), currenttokeninparagraph, currenttokeninparagraph)
                messages.append(spellcheckmessage(
                    suggestions, word, line,
                    contenthighlighted, contextid, basefile,
                    messagetype))

    return messages


def spellcheckmessage(suggestions, word, line, content,
                        contextid, basefile, messagetype):
    """ Create a message after a spell check has found a non-dictionary word.

    :param list suggestions: list of strings with suggestions
    :param str word: spelling, as actually used
    :param int line: line number (generally wrong at the moment)
    :param str content: paragraph of text that "word" appears in
    :param str contextid: value of id attribute on next node
    :param str basefile: name of file that "word" appears in
    :param str messagetype: print 'error', 'warning', or 'info' message?
    """

    # FIXME: shorten content string (in the right place), to get closer toward
    # more focused results
    message = None
    filename = ""
    if basefile:
        filename = "<file>%s</file>" % str(basefile)

    withinid = ""
    if contextid:
        withinid = "<withinid>%s</withinid>" % str(contextid)

    message = etree.XML("""<result type="%s">
            <location>%s%s<line>%s</line></location>
        </result>""" % (messagetype, filename, withinid, str(line)))

    message.append(etree.XML("""<message>Do not use
        <quote>%s</quote>:
        <quote>%s</quote></message>""" % (word, content)))

    if suggestions:
        # Sometimes enchant will give eight or ten suggestions. This clutters
        # the view quite a bit, so show at most 5 suggestions -- still not
        # quite sure if this is a good idea, though: Sometimes relevant
        # suggestions are removed because of this.
        for suggestion in suggestions[:5]:
            message.append(etree.XML("""<suggestion>Correct to
                <quote>%s</quote>.</suggestion>""" % suggestion))

    return message
