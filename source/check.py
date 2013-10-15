#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# This might check style & grammar one day. I'm hopeful. Kinda.

import sys, os, subprocess, shutil
from lxml import etree
# import pdb

openfile = False
dcfile = False
resultpath = "/tmp/"
arguments = sys.argv
location = os.path.dirname(os.path.realpath(__file__)) + '/'

# Handle arguments
if ( "--help" in arguments ) or ( "-h" in arguments ):
  sys.exit( """Usage: %s [OPTIONS] FILE

Options:
      --dc  Use a DC file as input, this will invoke DAPS to create a bigfile
    --open  Open final report in $BROWSER
 --version  Print version number
    --help  Show this screen""" % arguments[0] )

if ( "--version" in arguments ) or ( "-v" in arguments ):
  sys.exit( "Documentation Style Checker 0.1.0pre" )

if ("--open" in arguments ) or ( "-o" in arguments ):
  if ( os.environ.get('BROWSER') == None ):
    sys.exit( "Before using the --open option, do: export BROWSER=\"MY/FAVORITE/BROWSER\"" )
  openfile = True
  arguments = list(filter(('--open').__ne__, arguments))
  arguments = list(filter(('-o').__ne__, arguments))

if ("--dc" in arguments) or ( "-d" in arguments ):
  dcfile = True
  resultpath = "build/.tmp/"
  arguments = list(filter(('--dc').__ne__, arguments))
  arguments = list(filter(('-d').__ne__, arguments))

if len( arguments ) < 2:
  sys.exit( """Not enough arguments provided.
Usage: %s [OPTIONS] FILE
To see all options, do: %s --help""" % ( arguments[0], arguments[0] ) )

if not os.path.exists( arguments[-1] ):
  sys.exit( "File %s does not exist.\n" % arguments[-1] )


inputfile = arguments[-1]

# Some crazy DAPS integration
if dcfile == True:
  inputfile = (subprocess.check_output( [ 'daps', '-d', arguments[-1], 'bigfile' ] )
              .decode( 'UTF-8' ) ).replace( '\n', '' )

# pdb.set_trace()

output = etree.XML('<?xml-stylesheet type="text/css" href="check.css"?><results></results>')
rootelement = output.xpath( '/results' )

# Checking via XSLT
parser = etree.XMLParser(ns_clean=True,
                         remove_pis=False,
                         dtd_validation=False)
inputfile = etree.parse( inputfile, parser )
transform = etree.XSLT( etree.parse( location + 'xsl-checks/procedure-steps.xsl', parser ) )
result = transform( inputfile ).getroot()

print(rootelement[0])

if not result == None:
  output = rootelement[0].append(result)
print(output)


# output.getroottree().write( resultpath + 'checkresult.xml',
#               xml_declaration=True,
#               encoding="UTF-8",
#               pretty_print=True)

# shutil.copyfile( location + 'check.css', resultpath + 'checkresult.css' )

# if openfile == True:
#   subprocess.call( [ os.environ['BROWSER'] , resultpath + 'checkresult.xml' ] )