#
# Copyright (c) 2015-2016 SUSE Linux GmbH
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#

from lxml import etree

# Prepare parser (add py: namespace)
GITHUB_NS= 'https://www.github.com/openSUSE/suse-doc-style-checker'
SDSCNS = etree.FunctionNamespace(GITHUB_NS)
SDSCNS.prefix = 'py'

# FIXME: Update here the dictionary with XSLT extension functions
#SDSCNS.update(dict(linenumber=linenumber,
#                   termcheck=termcheck,
#                   buildtermdata=buildtermdata,
#                   dupecheck=dupecheck,
#                   sentencelengthcheck=sentencelengthcheck,
#                   sentencesegmenter=sentencesegmenter,
#                   tokenizer=tokenizer,
#                   counttokens=counttokens,
#                   splitpath=splitpath))


XMLParser = etree.XMLParser(ns_clean=True,
                            remove_pis=False,
                            dtd_validation=False)
