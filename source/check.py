#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# This might check style & grammar one day. I'm hopeful. Kinda.

import sys, os.path, subprocess, webbrowser, glob, re
from lxml import etree

programname = "Documentation Style Checker"
programversion = "0.1.0pre"

openfile = False
dcfile = False

# TODO: make this path more OS-agnostic
resultpath = "/tmp"
arguments = sys.argv
location = os.path.dirname( os.path.realpath(__file__) )

# Handle arguments
# TODO: Use argparse module
if ( "--help" in arguments ) or ( "-h" in arguments ):
  sys.exit( """Checks a given DocBook XML file or DAPS DC file for
stylistic errors.

Usage: %s [OPTIONS] FILE

Options:
      --dc  -d  Use a DC file as input, this will invoke DAPS to create a
                bigfile.
    --open  -o  Open final report in $BROWSER, or default browser if unset.
                Not all browsers open report files correctly and for some
                users, a text editor will open. In such cases, set the
                BROWSER variable with: export BROWSER=/MY/FAVORITE/BROWSER
                Chromium or Firefox will both do the right thing.
 --version  -v  Print version number.
    --help  -h  Show this screen.
""" % arguments[0] )

if ( "--version" in arguments ) or ( "-v" in arguments ):
  sys.exit( programname + " " + programversion )

if ("--open" in arguments ) or ( "-o" in arguments ):
  openfile = True
  arguments = list(filter(('--open').__ne__, arguments))
  arguments = list(filter(('-o').__ne__, arguments))

if ("--dc" in arguments) or ( "-d" in arguments ):
  dcfile = True
  arguments = list(filter(('--dc').__ne__, arguments))
  arguments = list(filter(('-d').__ne__, arguments))

if len( arguments ) < 2:
  sys.exit( """Not enough arguments provided.
Usage: %s [OPTIONS] FILE
To see all options, do: %s --help""" % ( arguments[0], arguments[0] ) )

if not os.path.exists( arguments[-1] ):
  sys.exit( "File %s does not exist.\n" % arguments[-1] )


inputfile = arguments[-1]

resultfilename = os.path.basename( os.path.realpath( inputfile ) )
resultfilename = re.sub( r'(([Dd][Cc]|[Ee][Nn][Vv])-|(_bigfile)?\.xml)', r'', resultfilename )
resultfilename = 'style-check-%s.xml' % resultfilename

# TODO: separate input file name from path & prepend that to output file name

# Some crazy DAPS integration
if dcfile == True:
  resultpath = os.path.join( os.path.dirname( os.path.realpath( inputfile ) ), "build", ".tmp" )
  inputfile = ( subprocess.check_output( [ 'daps', '-d', inputfile, 'bigfile' ] )
              .decode( 'UTF-8' ) ).replace( '\n', '' )

output = etree.XML('<?xml-stylesheet type="text/css" href="%s"?><results></results>'
                    % os.path.join( location, 'check.css' ) )
rootelement = output.xpath( '/results' )

rootelement[0].append( etree.XML( '<results-title>Style Checker Results</results-title>' ) )


# Checking via XSLT

parser = etree.XMLParser( ns_clean=True,
                          remove_pis=False,
                          dtd_validation=False )
inputfile = etree.parse( inputfile, parser )

for checkfile in glob.glob( os.path.join( location, 'xsl-checks', '*.xslc' ) ):
  transform = etree.XSLT( etree.parse( checkfile, parser ) )
  result = transform( inputfile ).getroot()

  if not ( len( result.xpath( '/part/result' ) ) ) == 0 :
    rootelement[0].append(result)

resultfile = os.path.join( resultpath, resultfilename )

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
