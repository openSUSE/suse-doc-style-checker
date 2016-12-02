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
from .cli import parseargs
from .color import printcolor
from .version import __version__
from .regex import (parentheses, sentenceends, lastsentenceends,
                   emptysubpattern, re_compile)
from .parser import XMLParser, SDSCNS
from .xslt import (counttokens,
                   # buildtermdata,
                   dupecheck,
                   linenumber,
                   splitpath,
                   sentencelengthcheck,
                   sentencesegmenter,
                   # termcheck,
                   tokenizer,
                   )
from .xslt import (canBeDupe,
                   findtagreplacement,
                   highlight,
                   isDupe,
                   removepunctuation,
                   xmlescape,
                   )


# Global flags
flag_performance = False
flag_checkpatterns = False
flag_module = False



def sanitizepunctuation(text, quotes=False, apostrophes=False):
    """Ensures that we always work on the same kind of quotes and apostrophes.

    Parameters:
    text   - str() of text that we want to look at
    quotes - bool(): quotes should quotes be sanitized?
    apos   - bool(): quotes should apostrophes be sanitized?
    """

    if quotes:
        # FIXME: In enough cases, using this will lose the information whether this
        # was a opening quote or a closing quote.
        # Replace quotes only if they are at start/end of a word.
        quote = re_compile(r'((?<=^)[«»‹›“”„‟‘’‚‛「」『』](?=[a-z0-9])|(?<=\s)[«»‹›“”„‟‘’‚‛「」『』](?=[a-z0-9])|(?<=[a-z0-9])[«»‹›“”„‟‘’‚‛「」『』](?=$|\s))', re.I)
        text = quote.sub('"', text)
    if apostrophes:
        apostrophe = re_compile(r'[’՚\'ʼ＇｀̀́`´ʻʹʽ]')
        text = apostrophe.sub('\'', text)
    return text


def termcheck(context, termfileid, content, contentpretty, contextid, basefile,
              messagetype):
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
    if not messagetype == 'warning' or messagetype == 'info':
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
    if onepattern:
        if not onepattern.search(content):
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
                    acceptword = accept[0]
                    acceptcontext = accept[1]

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
    useonepatterntemp = True
    if useonepattern:
        if useonepattern[0] == 'no':
            useonepatterntemp = False
    useonepattern = useonepatterntemp

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

    accepts = [prepareaccept(term) for term in terms]
    patterns = [preparetermpatterns(term, useonepattern) for term in terms]

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

        tryresult = emptysubpattern.search(pattern)
        if tryresult:
            message = "Part of Expression matches empty string"
            sys.exit(1)
    except SystemExit:
        expressionerror(message, pattern)

    return True


def expressionerror(message, expression="muschebubu"):
    printcolor(message + ": \"" + expression + "\"", 'error')
    sys.exit(1)


def manglepattern(pattern, mode):
    # Use (?: to create non-capturing groups: the re module's
    # implementation only supports up to 100 named groups per
    # expression. onepattern often contains more than 100 groups.
    if mode == 'one':
        pattern = parentheses.sub('(?:', pattern)

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
    printcolor("There is an empty {0} element in a terminology file.".format(element), 'error')
    sys.exit(1)


def termcheckmessage(acceptword, acceptcontext, word, line, content,
                        contextid, basefile, messagetype):
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


# This list is filled by initialize() with the following entries:
# { 'name': 'typos', 'transform': <function> }
prepared_checks = []

# Global parser instance. Initialized by initialize()
# parser = None


def checkOneFile(inputfilepath):
    """Checks one XML file and returns the result as XML. """

    location = os.path.dirname(os.path.realpath(__file__))
    inputfilename = os.path.basename(inputfilepath)
    output = etree.XML("""<?xml-stylesheet type="text/css" href="%s"?>
                            <results/>"""
                      % os.path.join(location, 'check.css'))

    resultstitle = etree.Element('results-title')
    resultstitle.text = "Style Checker Results for %s" % inputfilename
    output.append(resultstitle)

    # Checking via XSLT
    inputfile = etree.parse(inputfilepath, XMLParser)

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
    to avoid doing it for each file. """
    global sdsc_initialized
    if sdsc_initialized:
        return True

    # Update namespace dictionary with XSLT extension functions
    # TODO: Move this into a separate file
    SDSCNS.update(dict(#linenumber=linenumber,
                       termcheck=termcheck,
                       buildtermdata=buildtermdata,
                       #dupecheck=dupecheck,
                       #sentencelengthcheck=sentencelengthcheck,
                       #sentencesegmenter=sentencesegmenter,
                       #tokenizer=tokenizer,
                       #counttokens=counttokens,
                       #splitpath=splitpath
                       ))


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
            transform = etree.XSLT(etree.parse(checkfile, XMLParser))
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
