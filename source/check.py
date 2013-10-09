#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# This might check style & grammar one day. I'm hopeful. Kinda.

import sys, os, subprocess, shutil
from lxml import etree

if len( sys.argv ) < 2:
  sys.exit( "No file provided.\nUsage: %s FILE" % sys.argv[0] )
if sys.argv[1] == "--help" or sys.argv[1] == "-h":
  sys.exit( "Usage: %s FILE" % sys.argv[0] )
if sys.argv[1] == "--version" or sys.argv[1] == "-v":
  sys.exit( "Style Checker 0.1.0" )
if not os.path.exists( sys.argv[1] ):
  sys.exit( "File %s provided does not exist.\n" % sys.argv[1] )
else:
  inputfile = etree.parse( sys.argv[1] )
  transform = etree.XSLT( etree.parse( "/home/work/svn/stylecheck/source/check.xsl" ) )
  result = transform( inputfile )

  estring = etree.tostring( result, pretty_print=True )
  prettyformat = '<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet type="text/css" href="checkresult.css" ?>'
  resultfile = open( '/tmp/checkresult.xml', 'w' )
  resultfile.write( prettyformat + estring.decode('UTF-8') )
  resultfile.close()
  shutil.copyfile( 'check.css', '/tmp/checkresult.css' )

  subprocess.call(['firefox', '/tmp/checkresult.xml'])