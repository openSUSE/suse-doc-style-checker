#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import argparse
import glob
import os.path
import re
import subprocess
import sys
import time
import argparse
import webbrowser
try:
    from lxml import etree
except ImportError:
    sys.exit("Could not import from LXML. Is LXML for Python 3 installed?")

__programname__ = "Documentation Style Checker"
__version__ = "0.1.0pre"
__author__ = "Stefan Knorr"
__license__ = "MIT"
__description__ = "checks a given DocBook XML file for stylistic errors"

# global variables
args = None
# terminology data structures
termdataid = None
acceptpatterns = []
matchpatterns = []      # per acceptpattern, add list of matchpatterns
contextpatterns = []    # per matchpattern, add list of contextpatterns


# TODO: Get rid of the entire "positional arguments" thing that argparse adds
# (self-explanatory anyway). Get rid of "optional arguments" header. Make sure
# least important options (--help, --version) are listed last. Also, I really
# liked being able to use sentences in the parameter descriptions.
def parseargs():
    parser = argparse.ArgumentParser(
        usage = __file__ + " [options] inputfile [outputfile]",
        description = __description__ )
    parser.add_argument('-v', '--version',
        action = 'version',
        version = __programname__ + " " + __version__,
        help = "show version number and exit")
    parser.add_argument( '-s', '--show',
        action = 'store_true',
        default = False,
        help = """show final report in $BROWSER, or default browser if unset; not
            all browsers open report files correctly and for some users, a text
            editor will open; in such cases, set the BROWSER variable with:
            export BROWSER=/MY/FAVORITE/BROWSER ; Chromium or Firefox will both
            do the right thing""" )
    parser.add_argument( '-e', '--errors',
        action = 'store_true',
        default = False,
        help = """output error messages, but do not output warning or
            information messages""" )
    parser.add_argument( '--performance',
        action = 'store_true',
        default = False,
        help = "write some performance measurements to stdout" )
    parser.add_argument( 'inputfile' )
    parser.add_argument( 'outputfile', nargs = "?" )

    return parser.parse_args()

def printcolor( message, type = None ):
    if sys.stdout.isatty():
        if type == 'error':
            print( '\033[0;31m' + message + '\033[0m' )
        else:
            print( '\033[0;32m' + message + '\033[0m' )
    else:
        print( message )

def linenumber( context ):
    return context.context_node.sourceline

def termcheck( context, termfileid, terms, content ):
    # FIXME: Modes: para, title?
    # FIXME: Use fileid to skip creation of data structures
    messages = []

    if content:
        global termdataid
        global acceptpatterns
        global matchpatterns
        global contextpatterns

        # FIXME: Get something better than s.split. It is actually quite
        # important to get (most) sentence boundaries in the future. Some
        # existing tokenisers are overzealous, such as the default one from
        # NLTK.
        words = content[0].split()
        wordposition = 0
        totalwords = len( words )

        if args.performance:
            timestartbuild = time.time()

        if not termfileid == termdataid:
            buildtermdata( termfileid, terms )

        if args.performance:
            timestartmatch = time.time()

        for word in words:
            # When a pattern already matches on a word, don't try to find more
            # problems with it. (Is that a sane approach? Maybe there are other
            # problems...)
            # FIXME: I was unsure how to use continue to do this. Essentially,
            # depending on a wordmatch appearing, I need to skip up two
            # loops. :/
            trynextterm = True

            # Use the *patterns variables defined above to match all patterns
            # over everything.
            # FIXME: An optimisation should be to first get the first letter of
            # the word, then apply all patterns that starts with that letter.
            # However, the the information which letter any pattern belongs to
            # must probably be built by hand.
            acceptposition = 0
            matchgroupposition = 0
            for acceptpattern in acceptpatterns:
                if trynextterm == True:

                    matchgroupstoacceptpattern = matchpatterns[ acceptposition ]
                    for matchgrouppattern in matchgroupstoacceptpattern:
                        matchword = matchgrouppattern.match( word )

                        contextwords = []
                        contextstomatchgroup = contextpatterns[ matchgroupposition ]
                        if matchword:
                            if acceptpattern and not contextstomatchgroup[0]:
                                acceptword = acceptpattern.match( word )
                                if acceptword:
                                    # matches accept pattern and there are no
                                    # context conditions => false positive
                                    continue
                            if not contextstomatchgroup[0]:
                                trynextterm = False
                                # easy positive
                                line = linenumber ( context )
                                messages.append( termcheckmessage(
                                    acceptpattern, word, line, content[0] ) )
                            else:
                                for contextpattern in contextstomatchgroup:
                                    if contextpattern[0]:
                                        contexttype = contextpattern[1]
                                        contextposition = wordposition

                                        # FIXME: after & before need to be handled
                                        if contexttype == 'previous':
                                            contextposition -= 1
                                        elif contexttype == 'next':
                                            contextposition += 1

                                        if ( contextposition < 0 or contextposition > ( totalwords - 1 ) ):
                                            continue
                                        else:
                                            contextword = contextpattern[0].match( words[ contextposition ] )
                                            if contextword != None:
                                                contextwords.append( contextword )
                                        if ( len( contextstomatchgroup ) == len( contextwords )):
                                            line = linenumber ( context )
                                            message = termcheckmessage(
                                                acceptpattern, word, line,
                                                content[0] )
                                            messages.append( message )
                                        trynextterm = False

                        matchgroupposition += 1
                acceptposition += 1

            wordposition += 1

        if args.performance:
            timeend = time.time()
            timediffbuild = timestartmatch - timestartbuild
            timediffmatch = timeend - timestartmatch
            timedifftotal = timeend - timestartbuild
            print( """words: %s
time (total): %s
to build: %s (%s %%)
per word: %s"""
                % ( str( totalwords ), str( timedifftotal ),
                    str( timediffbuild ),
                    str( timediffbuild / timedifftotal * 100 ),
                    str( timediffmatch / (totalwords + .01 ) ) ) )

    return messages

def buildtermdata( termfileid, terms ):

    global termdataid
    global acceptpatterns
    global matchpatterns
    global contextpatterns

    termdataid = termfileid

    for term in terms:
        acceptxpath = term.xpath( 'accept[1]' )
        acceptxpathcontent = acceptxpath[0].text
        if acceptxpathcontent:
            acceptpattern = re.compile( acceptxpathcontent )
            acceptpatterns.append( acceptpattern )
        else:
            acceptpatterns.append( None )

        matchpatternsofterm = []
        matchgroupxpaths = term.xpath( 'matchgroup' )
        for matchgroupxpath in matchgroupxpaths:
            matchxpathcontent = matchgroupxpath.xpath( 'match[1]' )[0].text
            if not matchxpathcontent:
                emptypatternmessage( 'match' )
            matchpattern = re.compile( matchxpathcontent, flags = re.I )
            matchpatternsofterm.append( matchpattern )

            contextpatternsofmatchgroup = []
            contextxpaths = matchgroupxpath.xpath( 'context' )
            if contextxpaths:
                for contextxpath in contextxpaths:
                    contextxpathcontent = contextxpath.text
                    if not contextxpathcontent:
                        emptypatternmessage( 'context' )
                    contextpattern = re.compile(
                        contextxpathcontent, flags = re.I )
                    contexttype = contextxpath.xpath( '@type' )[0]
                    contextpatternsofmatchgroup.append(
                        [ contextpattern, contexttype ] )
            else:
                contextpatternsofmatchgroup.append( [ None ] )
            contextpatterns.append( contextpatternsofmatchgroup )

        matchpatterns.append( matchpatternsofterm )
    return None

def emptypatternmessage( element ):
    sys.exit( """Terminology: There is an empty %s element.
Make sure each %s element in the terminology file(s) contains a pattern."""
        % (element, element) )

def termcheckmessage( acceptpattern, word, line, content ):
    # FIXME: shorten content string
    message = None
    if acceptpattern:
        message = etree.XML( """<result>
                <error>Use %s instead of %s <place><line>%s</line></place>:
                    <quote>%s</quote>
                </error>
            </result>""" % ( acceptpattern.pattern, word, line, content ) )
    else:
        message = etree.XML( """<result>
                <error>Do not use %s <place><line>%s</line></place>:
                    <quote>%s</quote>
                </error>
            </result>""" % ( word, line, content ) )
    return message


def main():

    ns = etree.FunctionNamespace(
        'https://www.gitorious.org/style-checker/style-checker' )
    ns.prefix = 'py'
    ns[ 'linenumber' ] = linenumber
    ns[ 'termcheck' ] = termcheck

    location = os.path.dirname( os.path.realpath( __file__ ) )

    global args
    args = parseargs()

    if args.outputfile:
        resultfilename = args.outputfile
        resultpath = os.path.dirname( os.path.realpath( args.outputfile ) )
    else:
        resultfilename = args.inputfile
        resultfilename = os.path.basename( os.path.realpath( resultfilename ) )
        resultfilename = re.sub( r'(_bigfile)?\.xml', r'', resultfilename )
        resultfilename = '%s-stylecheck.xml' % resultfilename
        resultpath = os.path.dirname( os.path.realpath( args.inputfile ) )

    resultfile = os.path.join( resultpath, resultfilename )

    output = etree.XML(  """<?xml-stylesheet type="text/css" href="%s"?>
                            <results></results>"""
                      % os.path.join( location, 'check.css' ) )
    rootelement = output.xpath( '/results' )

    rootelement[0].append( etree.XML(
            "<results-title>Style Checker Results</results-title>" ) )


    # Checking via XSLT

    parser = etree.XMLParser(   ns_clean = True,
                                remove_pis = False,
                                dtd_validation = False )
    inputfile = etree.parse( args.inputfile, parser )

    for checkfile in glob.glob( os.path.join(   location,
                                                'xsl-checks',
                                                '*.xslc' ) ):
        transform = etree.XSLT( etree.parse( checkfile, parser ) )
        result = transform( inputfile )

        if args.errors == True:
            # FIXME: The following could presumably also be done without adding
            # a separate stylesheet. Not sure if that would be any more
            # performant.
            errorstylesheet = os.path.join( location, 'errorsonly.xsl' )
            errortransform = etree.XSLT( etree.parse( errorstylesheet, parser ) )
            result = errortransform( result )

        result = result.getroot()

        if not ( len( result.xpath( '/part/result' ) ) ) == 0 :
            rootelement[0].append( result )

    if ( len( output.xpath( '/results/part' ) ) ) == 0:
        rootelement[0].append( etree.XML(
             """<result>
                    <info>No problems detected.</info>
                    <suggestion>Celebrate!</suggestion>
                </result>""" ) )


    output.getroottree().write( resultfile,
                                xml_declaration = True,
                                encoding = 'UTF-8',
                                pretty_print = True )

    if args.show == True:
        webbrowser.open( resultfile, new = 0 , autoraise = True )

    printcolor( resultfile )


if __name__ == "__main__":
    main()
