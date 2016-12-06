#!/bin/bash

DB=$(xmlcatalog /etc/xml/catalog http://docbook.sourceforge.net/release/xsl/current/manpages/docbook.xsl | sed -r 's_^file:/+_/_')

# The echo really helps debugging when things go wrong and we also don't really
# want to try using a file called "No" as the stylesheets
echo "DocBook stylesheet path: $DB"
if [[ -f ${DB} ]]; then
  xsltproc --output sdsc.1 $DB suse-doc-style-checker.xml
else
  exit 1
fi
