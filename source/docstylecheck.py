#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys, os.path, subprocess, webbrowser, glob, re, argparse
from lxml import etree

__programname__ = "Documentation Style Checker"
__version__ = "0.1.0pre"
__author__ = "Stefan Knorr"
__license__ = "MIT"
__description__ = "checks a given DocBook XML file for stylistic errors"

openfile = False

arguments = sys.argv
location = os.path.dirname( os.path.realpath( __file__ ) )

# TODO: Get rid of the entire "positional arguments" thing that argparse adds
# (self-explanatory anyway). Get rid of "optional arguments" header. Make sure
# least important options (--help, --version) are listed last. Also, I really
# liked being able to use sentences in the parameter descriptions.
def parseargs():
   parser = argparse.ArgumentParser(
      usage= __file__ + " [options] inputfile [outputfile]",
      description=__description__ )
   parser.add_argument('-v', '--version',
      action = 'version',
      version = __programname__ + ' ' + __version__,
      help = "show version number and exit")
   parser.add_argument( '-s', '--show',
      action = 'store_true',
      default = False,
      help = """show final report in $BROWSER, or default browser if unset; not
          all browsers open report files correctly and for some users, a text
          editor will open; in such cases, set the BROWSER variable with:
          export BROWSER=/MY/FAVORITE/BROWSER ; Chromium or Firefox will both
          do the right thing""" )
   parser.add_argument( 'inputfile' )
   parser.add_argument( 'outputfile', nargs="?" )

   return parser.parse_args()

args = parseargs()
# print(args)

# Handle arguments
resultfilename = args.inputfile
resultfilename = os.path.basename( os.path.realpath( resultfilename ) )
resultfilename = re.sub( r'(_bigfile)?\.xml', r'', resultfilename )
resultfilename = 'style-check-%s.xml' % resultfilename
resultpath = os.path.dirname( os.path.realpath( args.inputfile ) )
resultfile = os.path.join( resultpath, resultfilename )



output = etree.XML('<?xml-stylesheet type="text/css" href="%s"?><results></results>'
                    % os.path.join( location, 'check.css' ) )
rootelement = output.xpath( '/results' )

rootelement[0].append( etree.XML( '<results-title>Style Checker Results</results-title>' ) )


# Checking via XSLT

parser = etree.XMLParser( ns_clean=True,
                          remove_pis=False,
                          dtd_validation=False )
inputfile = etree.parse( args.inputfile, parser )

for checkfile in glob.glob( os.path.join( location, 'xsl-checks', '*.xslc' ) ):
  transform = etree.XSLT( etree.parse( checkfile, parser ) )
  result = transform( inputfile ).getroot()

  if not ( len( result.xpath( '/part/result' ) ) ) == 0 :
    rootelement[0].append(result)

if ( len( output.xpath( '/results/part' ) ) ) == 0:
  rootelement[0].append( etree.XML( '<result><info>No problems detected.</info><suggestion>Celebrate!</suggestion></result>' ) )


output.getroottree().write( resultfile,
                            xml_declaration=True,
                            encoding="UTF-8",
                            pretty_print=True)

if openfile == True:
  webbrowser.open( resultfile, new=0 , autoraise=True )
else:
  print( resultfile )
