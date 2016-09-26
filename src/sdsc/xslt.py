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

from lxml import etree
import os.path

from .regex import (sentenceends, lastsentenceends, re_compile)

# termcheck
# buildtermdata
# dupecheck



# --------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------
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

    startpunctuation = '([{"\'¡¿'
    endpunctuation = ')]}/\\"\',:;!?.‥…‼‽⁇⁈⁉'

    if start:
        word = word.lstrip(startpunctuation)
    if end:
        word = word.rstrip(endpunctuation)
    return word


def canBeDupe(word):
    """TAGIGNORE: character sequences that should be ignored by the duplicate
    words check
    Ignored contents from tags can take either of the two forms below:
       ##@lowercase-1##
       ##@lowercase##
    The second form is counted as one token, the first one is counted as as many
    tokens as the number given after the dash."""

    numberignore = re_compile(r'[[{(\'"\s]*[-+]?[0-9]+(?:[.,][0-9]+)*[]})\'";:.\s]*')

    return len(word) > 0 and not numberignore.match(word) and not findtagreplacement(word)[0]


def isDupe(tokens, pos):
    """Returns how many tokens at pos are duplicated
       tokens = ["this", "is", "is", "a", "test"]
       pos = 2
       return 1"""
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


def highlight(tokens, highlightstart, highlightend):
    """TODO@sknorr

    :param tokens:

    Example:
       tokens = ["highlight", "these", "two", "words"]
       highlightstart = 1
       highlightend = 2
       return "highlight <highlight>these two</highlight> words"
       tokens can be a string as well, it will be tokenized automatically."""

    tokens = tokens[:] # toms: why?
    if isinstance(tokens, str):
        return highlight(tokenizer(tokens), highlightstart, highlightend)

    if highlightstart >= len(tokens) or highlightend < highlightstart:
        return ""  # Nothing to highlight

    highlightend = min(highlightend, len(tokens) - 1)

    tokens[highlightstart] = "<highlight>" + tokens[highlightstart]
    tokens[highlightend] = tokens[highlightend] + "</highlight>"

    return " ".join(tokens)


def xmlescape(text):
    """TODO@sknorr

    :param str text:
    """
    escapetable = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
        }
    return "".join(escapetable.get(c, c) for c in text)


def dupecheckmessage(context, quote, duplicate, contextid, basefile):
    """TODO@sknorr"""
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


# --------------------------------------------------------------------
# XSLT Extension Functions
# --------------------------------------------------------------------


def linenumber(context):
    """Returns the line number of the current context

    :param str context: Context node (ignored)
    """
    return context.context_node.sourceline


def splitpath(context, path, wantedsegment='filename'):
    """Split a path into segments and return the wanted segment.

    :param str context: Context node (ignored)
    :param str path: Input path or file name
    :param str wantedsegment: Segment that you want as output
        ('path' => path without file name and without trailing slash,
        'filename' => filename without extension,
        'extension' => file extension with leading dot and in lowercase)
    """

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


def counttokens(context, text):
    """TODO@sknorr:

    :param str context: Context node (ignored)
    """

    count = 0
    if text:
        count = len(tokenizer(text[0]))
    return count


def tokenizer(text):
    """TODO@sknorr: Splits text into words

    :param str text:
    """
    return text.split()


def sentencesegmenter(text):
    """TODO@sknorr:

    :param str text:
    """
    sentences = sentenceends.split(text)
    # The last sentence's final punctuation has not yet been cut off, do that
    # now.
    sentences[-1] = lastsentenceends.sub('', sentences[-1])

    # We also need to cut off parentheses etc. from the first word of the first
    # sentence, as that has not been done so far either.
    sentences[0] = removepunctuation(sentences[0], start=True)
    return sentences


def sentencelengthcheck(context, content, contentpretty, contextid, basefile,
                        lengthwarning, lengtherror):
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


def dupecheck(context, content, contentpretty, contextid, basefile):
    """TODO@sknorr
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

    #if flag_performance:
    #    timestartmatch = time.time()

    messages = []
    for wordposition, word in enumerate(words):
        dupeLen = isDupe(words, wordposition)
        if dupeLen == 0:
            continue  # No dupes found

        prettyTokens = tokenizer(xmlescape(contentpretty))
        quote = highlight(prettyTokens, indices[wordposition - dupeLen], indices[wordposition + dupeLen - 1])
        duplicate = xmlescape(" ".join(prettyTokens[indices[wordposition - dupeLen]:indices[wordposition]]))
        messages.append(dupecheckmessage(context, quote, duplicate, contextid, basefile))

    #if flag_performance and len(words) > 0:
    #    timediffmatch = time.time() - timestartmatch
    #    printcolor("""words: %s
#time for this para: %s
#average time per word: %s\n"""
    #        % (str(len(words)), str(timediffmatch),
    #            str(timediffmatch / len(words))), 'debug')

    return messages
