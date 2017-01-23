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

__programname__ = "SUSE Documentation Style Checker"
__version__ = "2016.7.0.0"
__author__ = "Stefan Knorr, Thomas Schraitle, Fabian Vogt"
__license__ = "LGPL-2.1+"
__description__ = "checks a given DocBook XML file for stylistic errors"

import glob
import os.path
import re
import sys
import time
import random
import webbrowser


from lxml import etree
# all module names in singular for predictability.
from .cli import printcolor, parseargs
from .generic import (linenumber,
                      re_compile,
                      )
from .const import PARENTHESES, SENTENCEENDS, LASTSENTENCEENDS, EMPTYSUBPATTERN
from .textutil import (counttokens,
                       findtagreplacement,
                       removepunctuation,
                       sanitizepunctuation,
                       tokenizer,
                       xmlescape,
                       )
from .struct import Accept, PatternGroup

# Global flags
flag_performance = False
flag_checkpatterns = False
flag_module = False


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


def termcheck(context, termfileid, content, contentpretty, contextid, basefile,
              messagetype):
    """ Check a paragraph using text-level checks involving regular
    expressions. If there is a match, issue a message.

    :param ??? text: information about the context node
    :param int termfileid: the expected ID of the terminology data; this is
        used to check whether terminology was correctly initialized via
        buildtermdata()
    :param str content: content, as formatted for the terminology check itself
    :param str contentpretty: content, as formatted for display in a message
    :param str contextid: next element with id attribute around the content
    :param str basefile: file in which content appears
    :param str messagetype: print a 'warning', 'info', or 'error' message?
    """

    # FIXME: Modes: para, title?

    if not content:
        return []

    assert int(termfileid[0]) == int(termdataid), "Terminology data was not correctly initialized."

    # I get this as a list with one lxml.etree._ElementUnicodeResult.
    # I need a single string.
    # For whatever reason, this made termcheckmessage() crash
    # happily and semi-randomly.
    content = sanitizepunctuation(str(content[0]), quotes=False, apostrophes=True)

    basefile = basefile[0] if basefile else None
    contextid = contextid[0] if contextid else None

    # sanitize this...
    if messagetype not in ('warning', 'info'):
        messagetype = 'error'

    # onepattern is a concatenated list of all patterns of the terminology
    # file which are within a pattern1 element
    # how useful is onepattern?
    #   + the overhead for onepattern is (currently) akin to adding 1 word
    #     to every paragraph
    #   + 30-40 % of paragraphs are skipped because of onepattern
    #   + the paragraphs skipped because of onepattern average at
    #     5-10 words
    #   = worst case: similar time, best case: slight win,
    #     more compliant documentation will tip the scale in our favour
    if onepattern and not onepattern.search(content):
        if flag_performance:
            printcolor("skipped entire paragraph\n", 'debug')
        return []

    # This if/else block should not be necessary (if there is content,
    # there should always also be pretty content, but that depends on the
    # XSLT used for checking). It hopefully won't hurt either.
    contentpretty = str(contentpretty[0]) if contentpretty else content

    # This should get us far enough for now
    sentences = sentencesegmenter(content)

    # HACK: the counter goes up for the first word already, i.e. token[0],
    # thus we just start at -1, so the first word gets to be 0.
    currenttokeninparagraph = -1

    messages = []
    for sentence in sentences:
        # FIXME: Get something better than s.split. Some
        # existing tokenisers are overzealous, such as the default one from
        # NLTK.
        words = tokenizer(sentence)
        totalwords = len(words)

        if flag_performance:
            timestartmatch = time.time()

        skipcount = 0
        for wordposition, word in enumerate(words):
            # If we hit a placeholder, e.g. ##@key-1##, the number
            # (here: 1) signifies the number of tokens this placeholder
            # replaces. If no placeholder found, tagtokens is 1.
            _, _, tagtokens = findtagreplacement(word)
            currenttokeninparagraph += tagtokens

            # Idea of skipcount: if we previously matched a multi-word pattern,
            # we can simply skip the next few words since they were matched
            # already.
            if skipcount > 0:
                skipcount -= 1
                continue

            word = removepunctuation(word, start=True)

            # don't burn time on checking small words like "the," "a," "of" etc.
            # (configurable from within terminology file)
            if ignoredpattern and ignoredpattern.match(word):
                continue

            # When a pattern already matches on a word, don't try to find more
            # problems with it.
            trynextterm = True

            # Use the *patterns variables defined above to match all patterns
            # over everything that is left.
            # Don't use enumerate with patterngroupposition, its value
            # depends on being defined in this scope.
            patterngroupposition = 0
            for acceptposition, accept in enumerate(accepts):
                if trynextterm:
                    acceptword = accept.context
                    acceptcontext = accept.proposal

                    # FIXME: variable names are a bit of a mouthful
                    patterngroupstoaccept = patterns[acceptposition]
                    for patterngrouppatterns in patterngroupstoaccept:
                        if not trynextterm:
                            break
                        if (wordposition + len(patterngrouppatterns)) > totalwords:
                            patterngroupposition += 1
                            continue
                        trycontextpatterns = True
                        matchwords = ""
                        # Don't use enumerate for patterngrouppatternposition,
                        # its value depends on breaks.
                        patterngrouppatternposition = 0
                        skipcounttemporary = 0
                        for patterngrouppattern in patterngrouppatterns:
                            patternposition = wordposition + patterngrouppatternposition
                            if patternposition > (totalwords - 1):
                                trycontextpatterns = False
                                break
                            matchword = None

                            # This if/else is a bit dumb, but we already did
                            # removepunctuation() on word, so it is not
                            # the same as words[ patternposition ] any more.
                            if patterngrouppatternposition == 0:
                                matchword = patterngrouppattern.match(word)
                            else:
                                matchword = patterngrouppattern.match(words[patternposition])
                            if matchword:
                                if patterngrouppatternposition != 0:
                                    # The first matched pattern should not make
                                    # us skip a word ahead.
                                    skipcounttemporary += 1
                                    matchwords += " "
                                matchwords += matchword.group(0)
                            else:
                                trycontextpatterns = False
                                break
                            patterngrouppatternposition += 1

                        contextpatternstopatterngroup = contextpatterns[patterngroupposition]
                        highlightstart = currenttokeninparagraph
                        highlightend = highlightstart + skipcounttemporary
                        patterngroupposition += 1
                        if not trycontextpatterns:
                            continue

                        matches = False
                        if contextpatternstopatterngroup[0][0] is None:
                            # easy positive
                            matches = True
                        else:
                            matches = True
                            for contextpattern in contextpatternstopatterngroup:
                                if not contextpattern[0] or not matchcontextpattern(words,
                                                        wordposition, totalwords,
                                                        patterngrouppatternposition,
                                                        contextpattern):
                                    matches = False
                                    break

                        if matches:
                            skipcount = skipcounttemporary
                            trynextterm = False
                            line = linenumber(context)
                            contenthighlighted = highlight(xmlescape(contentpretty), highlightstart, highlightend)
                            messages.append(termcheckmessage(
                                acceptword, acceptcontext, matchwords, line,
                                contenthighlighted, contextid, basefile,
                                messagetype))

    if flag_performance:
        timeendmatch = time.time()
        timediffmatch = timeendmatch - timestartmatch
        timeperword = 0 if totalwords < 1 else timediffmatch / totalwords

        printcolor("""words: %s
time for this para: %s
average time per word: %s\n"""
            % (str(totalwords), str(timediffmatch),
                str(timeperword)), 'debug')

    return messages


def matchcontextpattern(words, wordposition, totalwords,
                        patterngrouppatternposition, contextpattern):
    contextstring = ""
    for contextwhere in contextpattern[1]:
        contextposition = wordposition + contextwhere
        if contextwhere > 0:
            # patterngrouppatternposition is at 1,
            # even if there was just one pattern
            contextposition += patterngrouppatternposition - 1
        if contextposition >= 0 and contextposition <= (totalwords - 1):
            contextstring += str(words[contextposition]) + " "

    # We could check for an empty context
    # here and then not run any check,
    # but that would lead to wrong
    # results when doing negative
    # matching.

    match = bool(contextstring) and bool(contextpattern[0].search(contextstring))
    return bool(contextpattern[2]) == match


def preparetermpatterns(term, useonepattern):
    """ Prepare regular expression patterns contained in the <term/> elements
    of an XML source by extracting their main pattern and context patterns
    and appending the main pattern to onepattern (if use of onepattern is
    enabled)

    :param ??? term: XML source of one <term/> element
    :param bool useonepattern: use onepattern?
    """

    global onepattern
    patternsofterm = []
    patterngroupxpaths = term.xpath('patterngroup')
    for patterngroupxpath in patterngroupxpaths:
        preparedpatterns = preparepatterns(patterngroupxpath, useonepattern)
        if useonepattern:
            # use (?: to create non-capturing groups: the re module's
            # implementation only supports up to 100 named groups per
            # expression
            onepattern += '|(?:%s)' % (preparedpatterns[1])

        patternsofterm.append(preparedpatterns[0])

        contextpatternsofpatterngroup = []
        contextpatternxpaths = patterngroupxpath.xpath('contextpattern')
        if contextpatternxpaths:
            for contextpatternxpath in contextpatternxpaths:
                contextpatternsofpatterngroup.append(
                    preparecontextpatterns(contextpatternxpath))
        else:
            contextpatternsofpatterngroup.append([None])
        contextpatterns.append(contextpatternsofpatterngroup)

    return patternsofterm


def buildtermdata(context, terms, ignoredwords, useonepattern):
    """ From XML definitions containing regular expressions to check for
    terminology/wording, create Python data structures. While we could also
    read the XML definitions ad-hoc when checking terminology, that would be
    significantly slower.

    :param ??? context: information about context node
    :param list terms: <term/> elements from terminology file
    :param str ignoredwords: regular expression containing words that should be ignored globally
    :param bool onepattern: should onepattern be used? (onepattern is a large
        regular expression pattern that combines all the main search patterns
        into one)
    """

    del context  # not used

    # random ID to find out if the termdata is still up-to-date
    global termdataid

    # pattern of words that can be ignored right away
    global ignoredpattern

    # list of accepted terms:
    # accepts = [ [ 'proposal', 'context' ], [ 'proposal without context', None ], [ None, None ], ... ]
    #             <accept/> #1,              <accept/> #2,                         <accept/> #3
    global accepts
    accepts = []

    # list of main search patterns, per accepted term:
    # patterns = [ [ [ pattern, pattern, pattern ], [ pattern, pattern ] ], [ [ pattern, pattern ], ... ], ... ]
    #              <accept/> #1,                                            <accept/> #1
    #                <patterngroup/> #1,            <patterngroup/> #2,       <patterngroup/> #1
    global patterns
    patterns = []

    # list of contextpatterns, per patterngroup:
    # patterns = [ [ [ contextpattern, [-2,-1], True ], [ contextpattern, [1], False ], ... ], [], ... ]
    #              <patterngroup/> #1,                                                         <patterngroup/> #2
    #                <contextpattern/> #1
    #                                  position(s) of tokens to check relative to pattern1 [negative numbers => before]
    #                                           matching mode [True => positive, pattern has to appear at least once]
    #                                                   <contextpattern/> #2
    #                                                                     position(s) of tokens to check relative to last [positive numbers => after]
    #                                                                          matching mode [False => negative, pattern must not appear in any of given places]
    global contextpatterns
    contextpatterns = []

    # one long regular expression pattern is cheaper than many short ones,
    # onepattern tries to account for that, with varying degrees of success
    global onepattern

    # Not much use, but ... let's make this a real boolean.
    useonepattern = False if useonepattern and useonepattern[0] == 'no' else True

    onepattern = "" if useonepattern else None

    if flag_performance:
        timestartbuild = time.time()

    # FIXME: Obviously this needs to be done in a better way,
    # like an incrementing counter
    termdataid = random.randint(0, 999999999)

    if ignoredwords:
        trypattern(ignoredwords[0])
        ignoredpattern = re_compile(manglepattern(ignoredwords[0], 0),
                                    flags=re.I)
    else:
        ignoredpattern = False

    accepts = [Accept(*prepareaccept(term)) for term in terms]
    patterns = [PatternGroup(*preparetermpatterns(term, useonepattern)) for term in terms]

    if useonepattern:
        onepattern = onepattern[1:]

    if useonepattern:
        onepattern = re_compile(manglepattern(onepattern, 'one'), flags=re.I)

    if flag_performance:
        timeendbuild = time.time()
        printcolor("time to build: %s" % str(timeendbuild - timestartbuild), 'debug')
    return termdataid


# FIXME: This might be functionality better suited for a test case instead of
# built-in
def trypattern(pattern):
    """ Checks that none of the regular expression patterns is invalid or
    matches an empty string, before it is compiled.

    :param str pattern: regular expression to test
    """

    if not flag_checkpatterns:
        return True

    try:
        expression = re_compile(pattern, flags=re.I)
    except re.error as error:
        expressionerror("Syntax error in expression (%s)" % error, pattern)

    try:
        tryresult = expression.search("")
        if tryresult:
            message = "Expression matches empty string"
            sys.exit(1)

        tryresult = expression.search(" ")
        if tryresult:
            message = "Expression matches single space"
            sys.exit(1)

        tryresult = EMPTYSUBPATTERN.search(pattern)
        if tryresult:
            message = "Part of Expression matches empty string"
            sys.exit(1)
    except SystemExit:
        expressionerror(message, pattern)

    return True


def expressionerror(message, expression="muschebubu"):
    """ Print error message about an invalid regular expression.

    :param str message: message text
    :param str expression: expression that failed
    """
    printcolor(message + ": \"" + expression + "\"", 'error')
    sys.exit(1)


def manglepattern(pattern, mode):
    """ Modify regular expression patterns to work within our various
    pattern matching modes. (Potentially fraught with errors. Beware when writing patterns.)

    :param str pattern: the regular expression pattern
    :param str mode: 'context' for context pattern treatment, 'one' for
        onepattern treatment, anything else for regular treatment
    """

    # Use (?: to create non-capturing groups: the re module's
    # implementation only supports up to 100 named groups per
    # expression. onepattern often contains more than 100 groups.
    if mode == 'one':
        pattern = PARENTHESES.sub('(?:', pattern)

    # Both contextpattern and onepattern are realised with re.search(),
    # thus need some more information about where a token should really
    # start.
    if mode == 'context' or mode == 'one':
        # Lookbehinds need to have a fixed length, thus we use two (which makes
        # this more contrived than need be). There is no such requirement
        # for lookaheads.
        # Fwiw, below, we try to find places that are either at the beginning
        # of the string, have a space before them and optionally can also
        # have a non-word character directly before them, e.g. (.
        # The character class [\s^] does not work, thus we use (?:\s|^).
        pattern = r'((?<=^)(?:{0})|(?<=\s|^\W)(?:{0})|(?<=\s\W)(?:{0}))'.format(pattern)

    # And finally, let's see if there is any punctuation at the end. Looking
    # for the end of the string or a space makes sure we don't match e.g.
    # "just" in "just-installed".
    # This is enough for all words that are re.match()ed.
    pattern = (r'(?:%s)(?=\W{0,5}(?:\s|$))' % pattern)

    return pattern


def prepareaccept(term):
    """ From a <term/> element from XML source, extract the accepted spelling
    (<accept/>), and if available, its context (<context/>).

    :param ??? term: XML source of a <term/> element
    :return: tuple of (proposal, context)
    :rtype: tuple
    """

    acceptwordxpath = term.xpath('accept[1]/proposal[1]')
    acceptwordxpathcontent = None
    if acceptwordxpath:
        acceptwordxpathcontent = acceptwordxpath[0].text
    # If there is no accepted word, we don't care about the context
    if acceptwordxpathcontent:
        acceptlist = [acceptwordxpathcontent]
        acceptcontextxpath = term.xpath('accept[1]/context[1]')
        if acceptcontextxpath:
            acceptlist.append(acceptcontextxpath[0].text)
        else:
            acceptlist.append(None)

        return acceptlist
    else:
        return [None, None]


def preparepatterns(patterngroupxpath, useonepattern):
    """ Create a list of main patterns from a <patterngroup/> XML source.

    :param ??? patterngroupxpath: XML source of a <patterngroup/>
    :param bool useonepattern: use onepattern?
    """

    patternsofpatterngroup = []
    patternforonepattern = None

    lengthpatterngroupxpath = len(patterngroupxpath.xpath('pattern'))
    for i in range(1, lengthpatterngroupxpath + 1):
        patternxpath = patterngroupxpath.xpath('pattern[%s]' % i)
        patternxpathcontent = None
        if patternxpath:
            patternxpathcontent = patternxpath[0].text

        if not patternxpathcontent:
            if i == 1:
                emptypatternmessage('pattern')
            else:
                break
        else:
            trypattern(patternxpathcontent)
            if i == 1 and useonepattern:
                patternforonepattern = patternxpathcontent
            patternxpathcontent = manglepattern(patternxpathcontent, 'default')

        pattern = None
        if patternxpath[0].get('case') == 'keep':
            pattern = re_compile(patternxpathcontent)
        else:
            pattern = re_compile(patternxpathcontent, flags=re.I)
        patternsofpatterngroup.append(pattern)

    return [patternsofpatterngroup, patternforonepattern]


def contextpatternlocations(locations, factors, fuzzymode=False):
    """Returns locations to check for a contextpattern."""
    if fuzzymode:
        # Convert locations to ranges
        locations = [locr for loc in locations for locr in range(1, loc + 1)]

    # Apply all factors to all locations
    return [loc * factor for loc in locations for factor in factors]


def preparecontextpatterns(contextpatternxpath):
    """ Create Python structure for a context pattern from a
    <contextpattern/> XML source. This includes converting data whether the
    pattern is case-sensitive, and where it should be located in relation to
    the main pattern.

    :param ??? contextpatternxpath: XML source of a <patterngroup/>
    """

    contextpatternxpathcontent = contextpatternxpath.text
    if not contextpatternxpathcontent:
        emptypatternmessage('contextpattern')

    trypattern(contextpatternxpathcontent)

    # Since this is now searched for instead of matched on, we need to avoid
    # searching for e.g. "mail" in "e-mail".
    contextpatternxpathcontent = manglepattern(contextpatternxpathcontent, 'context')

    if contextpatternxpath.get('case') == 'keep':
        contextpattern = re_compile(contextpatternxpathcontent)
    else:
        contextpattern = re_compile(contextpatternxpathcontent, flags=re.I)

    factors = [1]
    if contextpatternxpath.get('look') == 'before':
        factors = [-1]
    elif contextpatternxpath.get('look') == 'bothways':
        factors = [-1, 1]

    fuzzymode = contextpatternxpath.get('mode') == 'fuzzy'
    positivematch = contextpatternxpath.get('match') != 'negative'

    locationxpath = contextpatternxpath.get('location')
    locations = [int(locationxpath)] if locationxpath else [1]
    locations = contextpatternlocations(locations, factors, fuzzymode)

    return [contextpattern, locations, positivematch]


def emptypatternmessage(element):
    """ Print a message if there is an empty XML source element, as that
    should not happen.

    :param str element: name of the element
    """

    printcolor("There is an empty {0} element in a terminology file.".format(element), 'error')
    sys.exit(1)


def termcheckmessage(acceptword, acceptcontext, word, line, content,
                        contextid, basefile, messagetype):
    """ Create a message after a terminology check has matched on something.

    :param str acceptword: accepted spelling
    :param str acceptcontext: context of accepted spelling
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

    if acceptcontext:
        message.append(etree.XML("""<message>In the context of %s,
            do not use <quote>%s</quote>:
            <quote>%s</quote></message>""" % (acceptcontext, word, content)))
    else:
        message.append(etree.XML("""<message>Do not use
            <quote>%s</quote> here:
            <quote>%s</quote></message>""" % (word, content)))

    if acceptword:
        message.append(etree.XML("""<suggestion>Use <quote>%s</quote>
            instead.</suggestion>""" % acceptword))
    else:
        message.append(etree.XML("""<suggestion>Remove
            <quote>%s</quote>.</suggestion>""" % word))

    return message


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

    if highlightstart >= len(tokens) or highlightend < highlightstart:
        return ""  # Nothing to highlight

    highlightend = min(highlightend, len(tokens) - 1)

    tokens[highlightstart] = "<highlight>" + tokens[highlightstart]
    tokens[highlightend] = tokens[highlightend] + "</highlight>"

    return " ".join(tokens)


def sentencelengthcheck(context, content, contentpretty, contextid, basefile,
                        lengthwarning, lengtherror):
    """Takes a paragraph, splits up sentences and checks whether the number
    of words in the sentences is longer than a defined maximum.
    """

    # Try to use sensible defaults. The following seems like better advice than
    # the SUSE Documentation Style Guide has to offer:
    # "Sometimes sentence length affects the quality of the writing. In general,
    # an average of 15 to 20 words is effective for most technical communication.
    # A series of 10-word sentences would be choppy. A series of 35-word
    # sentences would probably be too demanding. And a succession of sentences
    # of approximately the same length would be monotonous.
    # -- Mike Markel, Technical Communication, 9th ed. Bedford/St Martin's, 2010
    #    (via http://grammar.about.com/od/rs/g/Sentence-Length.htm)
    # However, it makes me think that we might be optimizing for the wrong metric
    # here. Otoh, it can't be good to allow 50-word or longer sentences. 35 words
    # does seem like some sort of boundary.

    maximumlengths = [24, 35]

    if lengthwarning:
        try:
            maximumlengths[0] = int(lengthwarning)
        except ValueError:
            printcolor('Sentence length check: Wrong type. Using default.', 'error')

    if lengtherror:
        try:
            maximumlengths[1] = int(lengtherror)
        except ValueError:
            printcolor('Sentence length check: Wrong type. Using default.', 'error')

    if not content:
        return []

    messages = []
    # I get this as a list with one lxml.etree._ElementUnicodeResult, not
    # as a list with a string.
    content = str(content[0])

    basefile = basefile[0] if basefile else None
    contextid = contextid[0] if contextid else None

    # This if/else block should not be necessary (if there is content,
    # there should always also be pretty content, but that depends on the
    # XSLT used for checking). It hopefully won't hurt either.
    contentpretty = str(contentpretty[0]) if contentpretty else content

    sentences = sentencesegmenter(content)
    # We need to find the current sentence inside of contentpretty by counting tokens.
    # In content, some tags like <command/> are replaced by
    # "##@command-<nr tokens>##" so we need to count that as well.
    sentencestart = 0
    sentenceend = 0

    for sentence in sentences:
        words = tokenizer(sentence)

        # Count tag replacements
        wordcount = 0
        for token in words:
            _, _, tagtokens = findtagreplacement(token)

            sentenceend += tagtokens
            # Tag placeholders count as max. 1 word.
            wordcount += min(1, tagtokens)

        if wordcount >= maximumlengths[0]:
            filename = "<file>{0}</file>".format(basefile) if basefile else ""
            withinid = "<withinid>{0}</withinid>".format(contextid) if contextid else ""
            messagetype = "error" if wordcount >= maximumlengths[1] else "warning"

            contentpretty = xmlescape(contentpretty)
            prettytokens = tokenizer(contentpretty)
            line = linenumber(context)
            highlightedcontent = highlight(prettytokens, sentencestart, sentenceend - 1)
            messages.append(etree.XML("""<result type="%s">
                            <location>%s%s<line>%s</line></location>
                            <message>Sentence with %s words:
                            <quote>%s</quote>
                        </message>
                        <suggestion>Remove unnecessary words.</suggestion>
                        <suggestion>Split the sentence.</suggestion>
                    </result>""" % (messagetype, filename, withinid, str(line),
                                    str(wordcount), highlightedcontent)))

        sentencestart = sentenceend

    return messages


def canBeDupe(word):
    """Checks if a word is eligible to be a duplicated word or if
    it should be ignored because it is actually a tag replacement.

    Ignored contents from tags can take either of the two forms below:
       ##@lowercase-1##
       ##@lowercase##
    The second form is counted as one token, the first one is counted as as many
    tokens as the number given after the dash.
    """

    numberignore = re_compile(r'[[{(\'"\s]*[-+]?[0-9]+(?:[.,][0-9]+)*[]})\'";:.\s]*')

    return len(word) > 0 and not numberignore.match(word) and not findtagreplacement(word)[0]


def isDupe(tokens, pos):
    """Returns how many tokens at pos are duplicated.

    tokens = ["this", "is", "is", "a", "test"]
    pos = 2
    return 1
    """
    # FIXME: Find a clever way to be able to check for variants of the same
    # word, such as: a/an, singular/plural, verb tenses. It should ideally
    # not be hardcoded here.
    maxlen = min(3, pos, len(tokens) - pos)
    tokens = tokens[:]
    for l in range(1, maxlen + 1):
        if not canBeDupe(removepunctuation(tokens[pos + l - 1], start=True, end=True)):
            return 0

        if removepunctuation(tokens[pos - l:pos], start=True) == removepunctuation(tokens[pos:pos + l], end=True):
            return l

    return 0


def dupecheckmessage(context, quote, duplicate, contextid, basefile):
    """Creates messages about duplicate words

    :param context:
    :param quote:
    :param duplicate:
    :param contextid: ID of the context
    :param basefile:
    :return: XML tree of the result
    """
    filename = ""
    if basefile:
        filename = "<file>%s</file>" % str(basefile)

    withinid = ""
    if contextid:
        withinid = "<withinid>%s</withinid>" % str(contextid)

    return etree.XML("""<result type="error">
            <location>%s%s<line>%s</line></location>
            <message><quote>%s</quote> is duplicated:
                <quote>%s</quote>
            </message>
            <suggestion>Remove one instance of <quote>%s</quote>.</suggestion>
        </result>""" % (filename, withinid, str(linenumber(context)), duplicate, quote, duplicate))


def dupecheck(context, content, contentpretty, contextid, basefile):
    """Takes a paragraph and checks it for duplicated words and phrases of up
    to three words in length.

    :param context:
    :param content:
    :param contentpretty:
    :param contextid:
    :param basefile:
    :return:
     """

    if not content:
        return []

    # I get this as a list with one lxml.etree._ElementUnicodeResult, not
    # as a list with a string.
    content = str(content[0])
    basefile = basefile[0] if basefile else None
    contextid = contextid[0] if contextid else None

    # This if/else block should not be necessary (if there is content,
    # there should always also be pretty content, but that depends on the
    # XSLT used for checking). It hopefully won't hurt either.
    contentpretty = str(contentpretty[0]) if contentpretty else content

    tokens = tokenizer(content.lower())
    # Get pretty indices
    wordtuples = []
    currentIndex = 0
    for word in tokens:
        wordtuples.append((currentIndex, word))
        _, _, tagtokens = findtagreplacement(word)
        currentIndex += tagtokens

    words = [word for index, word in wordtuples]
    indices = [index for index, word in wordtuples]

    if flag_performance:
        timestartmatch = time.time()

    messages = []
    for wordposition, word in enumerate(words):
        dupeLen = isDupe(words, wordposition)
        if dupeLen == 0:
            continue  # No dupes found

        prettyTokens = tokenizer(xmlescape(contentpretty))
        quote = highlight(prettyTokens, indices[wordposition - dupeLen], indices[wordposition + dupeLen - 1])
        duplicate = xmlescape(" ".join(prettyTokens[indices[wordposition - dupeLen]:indices[wordposition]]))
        messages.append(dupecheckmessage(context, quote, duplicate, contextid, basefile))

    if flag_performance and len(words) > 0:
        timediffmatch = time.time() - timestartmatch
        printcolor("""words: %s
time for this para: %s
average time per word: %s\n"""
            % (str(len(words)), str(timediffmatch),
                str(timediffmatch / len(words))), 'debug')

    return messages


def splitpath(context, path, wantedsegment='filename'):
    """Splits a path into segments and return the wanted segment.

    :param str context: Context node (ignored)
    :param str path: Input path or file name
    :param str wantedsegment: Segment that you want as output
        ('path' => path without file name and without trailing slash,
        'filename' => filename without extension,
        'extension' => file extension with leading dot and in lowercase)
    """

    del context # not used

    if not path:
        return []

    # I get this as a list with one lxml.etree._ElementUnicodeResult, not
    # as a list with a string.
    path = str(path[0])

    splitpath = os.path.split(path)
    splitfile = os.path.splitext(splitpath[1])

    if wantedsegment == 'path':
        return splitpath[0]
    elif wantedsegment == 'filename':
        return splitfile[0]
    elif wantedsegment == 'extension':
        return splitfile[1].lower().lstrip('.')
    else:
        return path

def splitvalueunit(context, value, part='value'):
    """ From a combination of numeric value and unit (like "100px"), returns
    either the value or the unit.

    :param str context: context node (ignored)
    :param str value: numeric value and unit
    :param str part: wanted part of input value: 'value' or 'unit'
    :return: numeric value or unit of input value
    """

    del context # not used

    value = str(value)
    part = str(part)

    regex_valueformat = re_compile(r'[.\d]+([a-z]{2,3}|%)?')
    regex_numericvalue = re_compile(r'^[.\d]+')
    regex_unit = re_compile(r'([a-z]{1,3}|%)$')

    if not value:
        return "MALFORMED_VALUE"
    if not regex_valueformat.fullmatch(value):
        return "MALFORMED_VALUE"

    if part == 'unit':
        unit = regex_unit.search(value)
        if unit:
            return unit.group(0)
        else:
            return ""
    else:
        # This should be guaranteed, since we check for regex_valueformat
        # before.
        numericvalue = regex_numericvalue.search(value)
        return numericvalue.group(0)


# This list is filled by initialize() with the following entries:
# { 'name': 'typos', 'transform': <function> }
prepared_checks = []

# Global parser instance. Initialized by initialize()
parser = None


def checkOneFile(inputfilepath):
    """Checks one XML file and returns the result as XML.
    """

    location = os.path.dirname(os.path.realpath(__file__))
    inputfilename = os.path.basename(inputfilepath)
    output = etree.XML("""<?xml-stylesheet type="text/css" href="%s"?>
                            <results/>"""
                      % os.path.join(location, 'check.css'))

    resultstitle = etree.Element('results-title')
    resultstitle.text = "Style Checker Results for %s" % inputfilename
    output.append(resultstitle)

    # Checking via XSLT
    inputfile = etree.parse(inputfilepath, parser)

    for check in prepared_checks:
        if flag_module or flag_performance:
            print("Running module {0!r}...".format(check["name"]))

        try:
            result = check["transform"](inputfile, moduleName=etree.XSLT.strparam(check["name"]))
        except Exception as error:
            printcolor("! Broken check file or Python function (module {0!r})".format(check["name"]), 'error')
            printcolor("  " + str(error), 'error')
            sys.exit(1)

        result = result.getroot()

        if result.xpath('/part/result'):
            output.append(result)

    if not output.xpath('/results/part'):
        output.append(etree.XML(
             """<result type="info">
                    <message>No problems detected.</message>
                    <suggestion>Celebrate!</suggestion>
                </result>"""))

    return etree.tostring(output.getroottree(),
                          encoding='unicode',
                          pretty_print=True)

# Flag to avoid multiple initialization
sdsc_initialized = False


def initialize():
    """ Initializes global values such as prepared_checks and parser
    to avoid doing it for each file.
    """

    global sdsc_initialized
    if sdsc_initialized:
        return True

    # Prepare parser (add py: namespace)
    ns = etree.FunctionNamespace('https://www.github.com/openSUSE/suse-doc-style-checker')
    ns.prefix = 'py'
    ns.update(dict(
        buildtermdata=buildtermdata,
        counttokens=counttokens,
        dupecheck=dupecheck,
        linenumber=linenumber,
        sentencelengthcheck=sentencelengthcheck,
        sentencesegmenter=sentencesegmenter,
        splitpath=splitpath,
        splitvalueunit=splitvalueunit,
        termcheck=termcheck,
        tokenizer=tokenizer,
    ))

    global parser
    parser = etree.XMLParser(ns_clean=True,
                             remove_pis=False,
                             dtd_validation=False)

    # Prepare all checks
    global prepared_checks
    prepared_checks = []
    location = os.path.dirname(os.path.realpath(__file__))
    checkfiles = glob.glob(os.path.join(location, 'xsl-checks', '*.xslc'))

    if not checkfiles:
        printcolor("! No check files found.\n  Add check files to " + os.path.join(location, 'xsl-checks'), 'error')
        return False

    for checkfile in checkfiles:
        try:
            checkmodule = os.path.splitext(os.path.basename(checkfile))[0]
            transform = etree.XSLT(etree.parse(checkfile, parser))
            prepared_checks.append({'name': checkmodule, 'transform': transform})
        except Exception as error:
            printcolor("! Syntax error in check file.\n  " + checkfile, 'error')
            printcolor("  " + str(error), 'error')

    sdsc_initialized = True
    return True


def main(cliargs=None):
    """Entry point for the application script

    :param list cliargs: Arguments to parse or None (=use sys.argv)
    """

    if not initialize():
        return 1

    timestart = time.time()

    location = os.path.dirname(os.path.realpath(__file__))

    global args
    try:
        args = parseargs(cliargs)
    except SystemExit as exc:
        return exc.code

    global flag_checkpatterns
    global flag_performance
    global flag_module
    flag_checkpatterns = args.checkpatterns
    flag_performance = args.performance
    flag_module = args.module

    if args.bookmarklet:
        webbrowser.open(
            os.path.join(location, 'result-flagging-bookmarklet.html'),
            new=0, autoraise=True)
        return 0

    if args.outputfile:
        resultfilename = args.outputfile
        resultpath = os.path.dirname(os.path.realpath(args.outputfile))
    else:
        resultfilename = re.sub(r'(_bigfile)?\.xml', r'', os.path.basename(args.inputfile.name))
        resultfilename = '%s-stylecheck.xml' % resultfilename
        resultpath = os.path.dirname(os.path.realpath(args.inputfile.name))

    resultfile = os.path.join(resultpath, resultfilename)
    with open(resultfile, 'w') as resultfh:
        try:
            result = checkOneFile(args.inputfile.name)
        except KeyboardInterrupt:
            printcolor("Operation cancelled!", 'error')
            return 1
        except etree.Error as error:
            printcolor("Syntax error in input: {0}!".format(error.msg), 'error')
            return 1

        resultfh.write(str(result))

    if args.show:
        webbrowser.open(resultfile, new=0, autoraise=True)

    printcolor(resultfile)
    if flag_performance:
        printcolor("Total: " + str(time.time() - timestart), 'debug')

    return 0
