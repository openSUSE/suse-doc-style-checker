#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# This might check style & grammar one day. I'm hopeful. Kinda.

import sys, os, subprocess, lxml

#if !( sys.argv[1] )
#  print "\nNo file provided."
#else
#  os.open( sys.argv[1] )
subprocess.call(['xsltproc', '--novalid', 'check.xsl', sys.argv[1]])