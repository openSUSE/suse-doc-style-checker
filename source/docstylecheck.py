#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys, os.path, subprocess, webbrowser, glob, re, argparse, time
from lxml import etree

__programname__ = "Documentation Style Checker"
__version__ = "0.1.0pre"
__author__ = "Stefan Knorr"
__license__ = "MIT"
__description__ = "checks a given DocBook XML file for stylistic errors"


# TODO: Get rid of the entire "positional arguments" thing that argparse adds
# (self-explanatory anyway). Get rid of "optional arguments" header. Make sure
# least important options (--help, --version) are listed last. Also, I really
# liked being able to use sentences in the parameter descriptions.
def parseargs():
    parser = argparse.ArgumentParser(
        usage = __file__ + " [options] inputfile [outputfile]",
        description=__description__ )
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
    parser.add_argument( 'inputfile' )
    parser.add_argument( 'outputfile', nargs="?" )

    return parser.parse_args()

def printcolor( message, type = None ):
    if sys.stdout.isatty():
        if type == 'error':
            print( "\033[0;31m" + message + "\033[0m" )
        else:
            print( "\033[0;32m" + message + "\033[0m" )
    else:
        print( message )

def linenumber( context ):
    return context.context_node.sourceline


# So slow. Like Dogecoin mine. Need much improve.
def termcheck( context, terms, content ):
    # modes: para, title?

    messages = [] # Do I actually need this? Probably, I want to return it.

    if content:
        # .split() (or better, but s.split will suffice for the moment.
        # However, it is actually quite important to get sentence boundaries
        # in the future. Some existing tokenisers are overzealous, such as
        # the default one from NLTK.
        words = content[0].split()
        wordposition = 0
        totalwords = len(words)

        for word in words:
            # I was unsure how to use continue to do this. Essentially,
            # depending on a wordmatch appearing, I need to skip up two
            # loops. :/
            trynextterm = True

            # Read in terminology.xml, match all patterns over everything. A
            # simple optimisation should be to first get the first letter o
            # the word, then apply everything that starts with that letter.
            for term in terms:
                if trynextterm == True:
                    accept = None
                    if term.xpath( "accept[1]" )[0].text:
                        accept = term.xpath( "accept[1]" )[0].text
                    matchgroups = term.xpath( "matchgroup[1]" )

                    for matchgroup in matchgroups:
                        match = matchgroup.xpath( "match[1]" )[0].text
                        wordmatch = re.match( match, word, flags=re.I )
                        acceptmatch = None
                        if accept != None:
                            acceptmatch = re.match( accept, word )

                        # Is this either a negative or false positive? Then save some effort.
                        if wordmatch != None and (acceptmatch == None or accept == None):
                            arounds = [] # Do I actually need this?
                            aroundmatches = []
                            if matchgroup.xpath( "around[1]" ):
                                arounds = matchgroup.xpath( "around" )
                                for around in arounds:
                                    around = matchgroup.xpath( "around[1]" )[0].text
                                    aroundtype = matchgroup.xpath( "around[1]/@type" )[0]
                                    aroundposition = wordposition
                                    # FIXME: after & before need to be handled separately
                                    if aroundtype == "next" or aroundtype == "after":
                                        aroundposition += 1
                                    elif aroundtype == "previous" or aroundtype == "before":
                                        aroundposition -= 1
                                    # elif aroundtype == "after":
                                    #     current+1 to [-1]
                                    # elif aroundtype == "before":
                                    #     [0] to current-1
                                    if not( aroundposition < 0 and aroundposition > ( totalwords - 1 ) ):
                                        aroundmatch = re.match( around, words[aroundposition], flags=re.I )
                                        if aroundmatch != None:
                                            aroundmatches.append( aroundmatch )

                            if ( len( arounds ) == len( aroundmatches )):
                                line = linenumber ( context )
                                # FIXME: shorten content string
                                if accept != None:
                                    messages.append( etree.XML( "<result><error>Use %s instead of %s <place><line>%s</line></place>: <quote>%s</quote></error></result>" % ( accept, word, line, content[0] ) ) )
                                else:
                                    messages.append( etree.XML( "<result><error>Do not use %s <place><line>%s</line></place>: <quote>%s</quote></error></result>" % ( word, line, content[0] ) ) )
                                trynextterm = False
            wordposition += 1


    return messages

def main():

    ns = etree.FunctionNamespace('https://www.gitorious.org/style-checker/style-checker')
    ns.prefix = 'py'
    ns['linenumber'] = linenumber
    ns['termcheck'] = termcheck

    location = os.path.dirname( os.path.realpath( __file__ ) )

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

    parser = etree.XMLParser(   ns_clean=True,
                                remove_pis=False,
                                dtd_validation=False )
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
                                xml_declaration=True,
                                encoding="UTF-8",
                                pretty_print=True )

    if args.show == True:
        webbrowser.open( resultfile, new=0 , autoraise=True )

    printcolor( resultfile )


if __name__ == "__main__":
    main()
