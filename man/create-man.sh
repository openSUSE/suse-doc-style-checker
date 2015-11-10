#!/bin/bash

DB=$(xmlcatalog /etc/xml/catalog http://docbook.sourceforge.net/release/xsl/current/manpages/docbook.xsl)
DB=${DB#file:/}

xsltproc --output sdsc.1 $DB suse-doc-style-checker.xml