#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# This might check style & grammar one day. I'm hopeful. Kinda.

import sys, os, subprocess, shutil
from lxml import etree
import webbrowser

if len( sys.argv ) < 2:
  sys.exit( "No file provided.\nUsage: %s FILE" % sys.argv[0] )
if sys.argv[1] == "--help" or sys.argv[1] == "-h":
  sys.exit( "Usage: %s FILE" % sys.argv[0] )
if sys.argv[1] == "--version" or sys.argv[1] == "-v":
  sys.exit( "Style Checker 0.1.0" )
if not os.path.exists( sys.argv[1] ):
  sys.exit( "File %s provided does not exist.\n" % sys.argv[1] )

parser = etree.XMLParser(ns_clean=True,
                         remove_pis=False,
                         #resolve_entities=False,
                         dtd_validation=False)
inputfile = etree.parse( sys.argv[1] )
transform = etree.XSLT( etree.parse( "check.xsl", parser ) )
result = transform( inputfile )

#estring = etree.tounicode( result, pretty_print=True )
#resultfile = open( '/tmp/checkresult.xml', 'w' )
#resultfile.write( estring )
#resultfile.close()

root = result.getroot()
print("root:", root.getchildren() )

result.write( '/tmp/checkresult.xml', xml_declaration=True, encoding="UTF-8", pretty_print=True)

shutil.copyfile( 'check.css', '/tmp/checkresult.css' )

firefox = webbrowser.get("firefox")
firefox.open_new_tab(url="/tmp/checkresult.xml")
# subprocess.call(['firefox', '/tmp/checkresult.xml'])

# EOF
