#!/usr/bin/env python3
#
# poc = proof of concept
#
# HINT:
# This file is just a test and can be deleted once all functionality
# is implemented (also remove poc_confi.ini).
#
# HINT 2:
# If you want to see more or less debug output, open file poc_config.ini,
# locate section "logger_poc" and change the key "level" to "DEBUG" or
# "WARN" accordingly.
#
# See also:
# http://lxml.de/extensions.html#xpath-extension-functions

from functools import partial
import inspect
import logging
import logging.config
import os.path
import sys

from lxml import etree


#
__version__ = "0.1"
__author__ = "Thomas Schraitle"
__license__ = "LGPL-2.1+"

#
GITHUB_NS = 'https://www.github.com/openSUSE/suse-doc-style-checker'
GITHUB_PREFIX = 'py'
#
HEREDIR = os.path.dirname(os.path.realpath(__file__))

#
# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger('poc').addHandler(logging.NullHandler())

logging.config.fileConfig(os.path.join(HEREDIR, 'poc_config.ini'),
                          disable_existing_loggers=False)
log = logging.getLogger('poc')


class MyXPathExtFunc:
    """Class which encapsulates XPath extension functions
    """
    # Add here your global variables...

    def test(self, context, arg):
        """Extension function test(arg)"""
        # Interesting side effect: when called from main_xslt
        # debug is not displayed. Strange...
        log.debug("MyXPathExtFunc.test called with: %s", arg)
        if isinstance(arg, list):
            arg = arg[0]
        if isinstance(arg, etree._Element):
            arg = arg.text
        return 'test' + arg


def getfunctions(cls):
    """Returns a tuple of all functions of a class 'cls', but ignores
       functions which starts with '_'

    :param cls: a class
    :return: a tuple containing function names as strings
    """
    # Extract first all names which doesn't start with '_'...
    names = (func for func in cls.__dict__ if not func.startswith('_'))
    # then check, if these names are possible functions:
    return tuple(f for f in names
                 if inspect.isfunction(cls.__dict__[f]))


def setup_namespace():
    """Setup namespace

    :return: dictionary with prefix:namespace entries
    """
    return {GITHUB_PREFIX: GITHUB_NS}


def setup_extensions(**args):
    """Setup XPath extension functions
    """
    functions = getfunctions(MyXPathExtFunc)
    module = MyXPathExtFunc()
    extensions = etree.Extension(module,
                                 functions,
                                 ns=GITHUB_NS
                                 )
    return extensions


def main_xslt():
    """Proof of concept of extension function in XSLT"""
    log.debug('Start.')
    XSLT = """<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:py="{NS}"
    exclude-result-prefixes="py">
  <xsl:template match="a">
    <A><xsl:value-of select="py:test(b)"/></A>
  </xsl:template>
</xsl:stylesheet>""".format(NS=GITHUB_NS)

    # Prepare stylesheet tree
    tree = etree.XML('<a><b>Hiho</b></a>').getroottree()
    style = etree.XML(XSLT)

    # Create transformation function, pass extension functions
    transform = etree.XSLT(style,
                           extensions=setup_extensions())
    result = transform(tree)
    log.debug("##### Result #####")
    print(etree.tostring(result, encoding="unicode"))
    log.debug('Finished.')


def main_xpath():
    """Proof of concept of extension function in XPath"""
    log.debug('Start.')

    tree = etree.XML('<a><b>Hiho</b></a>').getroottree()
    extensions = setup_extensions()
    ev = etree.XPathEvaluator(tree,
                              namespaces=setup_namespace(),
                              extensions=extensions
                              )
    log.debug("evaluator: %s", ev)
    log.debug("extensions: %s", extensions)
    log.debug("##### Result #####")
    print(ev("py:test('you')"))
    log.debug('Finished.')


if __name__ == "__main__":
    log.debug("Started...")
    try:
        main_xslt()
        log.debug("-"*30)
        main_xpath()
    except Exception as err:
        log.error(err, exc_info=True)
    log.debug("Finished.")
