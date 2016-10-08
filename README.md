Style Checker for SUSE Documentation
====================================

Tries as hard as its little mind can to check whether documentation is compliant with the
[SUSE Documentation Style Guide](https://github.com/SUSE/doc-styleguide). 

Releases are usually aligned with releases of the Style Guide.


Usage
-----

You can test the style checker from your Git checkout by executing:

```
$ PYTHONPATH=src python3 -m sdsc -h
```


Developing/Testing Releases
---------------------------

See the wiki for how to set up your test environment:

+ [Development Setup](https://github.com/sknorr/suse-doc-style-checker/wiki/Developing-SDSC)
+ [Python Virtual Environment](https://github.com/sknorr/suse-doc-style-checker/wiki/Initializing-Python3-Virtual-Environment)

Lucky Charms
------------

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/456aa12ad22b4550a9d91f34b850a3ea)](https://www.codacy.com/app/tomschr/suse-doc-style-checker?utm_source=github.com&utm_medium=referral&utm_content=openSUSE/suse-doc-style-checker&utm_campaign=badger)
[![Build Status](https://travis-ci.org/openSUSE/suse-doc-style-checker.svg?branch=develop)](https://travis-ci.org/openSUSE/suse-doc-style-checker)
[![Coverage Status](https://coveralls.io/repos/github/openSUSE/suse-doc-style-checker/badge.svg?branch=feature%2Fcoverage)](https://coveralls.io/github/openSUSE/suse-doc-style-checker?branch=feature%2Fcoverage)
[![Code Health](https://landscape.io/github/openSUSE/suse-doc-style-checker/develop/landscape.svg?style=flat)](https://landscape.io/github/openSUSE/suse-doc-style-checker/develop)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/openSUSE/suse-doc-style-checker/badges/quality-score.png?b=develop)](https://scrutinizer-ci.com/g/openSUSE/suse-doc-style-checker/?branch=develop)
