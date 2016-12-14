# Changelog

# Version 2016.7.0.0

### User-facing features:
* Support for language and structure rules from version 2016-07 of the
  SUSE Documentation Style Guide
* Support for DocBook 5 and GeekoDoc
* In the message display, the problematic parts are underlined
* Better performance
* Checks for references to images
* Finds more typos
* A large number of bug fixes

### Developer-facing features:

* SDSC is now Python module instead of a simple script
* There is now a test suite
* Large refactorings
* Many improvements in the release and packaging workflow
* The DTD for terminology files was adapted to be more flexible

### Detailed list of changes:

Find issues starting with sdsc# in the GitHub bug tracker:
 https://github.com/openSUSE/suse-doc-style-checker/issues
Find issues starting with doc-styleguide# in the GitHub bug tracker:
 https://github.com/SUSE/doc-styleguide/issues

Find issues starting with trello:style# in Trello:
 https://trello.com/b/VwQ41Lt0

* Terminology changes, corrections and additions (very incomplete list:
  trello:style#91, trello:style#69, trello:style#114, trello:style#113,
  trello:style#111, trello:style#99, trello:style#75, trello:style#88,
  trello:style#101, trello:style#94, doc-styleguide#2, doc-styleguide#12,
  doc-styleguide#34)
* Wordy phrases changes, corrections and additions (very incomplete list:
  trello:style#115)
* Typo check changes, corrections and additions
* Changes to the DTD and file format of terminology files (elements
  `pattern1` etc. are now called `pattern`, there are also new attribute names)
* All checks: Do not check legal texts (sdsc#121)
* Abbreviations: do not ignore some abbreviations (sdsc#56)
* Admonitions: correctly identify titles (sdsc#20)
* Command formatting: Do not recommend nesting command and option elements (sdsc#21)
* Duplicated words: ##@...## was not ignored in dupecheck() (sdsc#72)
* Duplicated words: add highlighting (sdsc#62)
* Duplicated words: do not fail because of punctuation (sdsc#52)
* Duplicated words: ignore standalone punctuation characters (sdsc#61)
* File name formatting: avoid message asking authors to move long `<filename/>`s into screens
* Keys: add more versions of textual left/right/tab/back key markup
* Long sentences: add highlighting (sdsc#38)
* Terminology: Add highlighting to words (related: sdsc#39)
* Figures: add checks for file name mishaps
* Sections: Do not complain about missing the construct `info/abstract` (sdsc#19, sdsc#104)
* Web addresses: Do not allow third-party URL shorteners

* Message display: allow displaying the ID of the element itself (sdsc#55)
* Base script: Catch KeyboardInterrupts (sdsc#73)
* Base script: moved namespace of XSLT extension functions to a GitHub URL (sdsc#9)
* Base script: use `sys.exit()` correctly (sdsc#11)
* Base script: use re_compile() for caching (related: sdsc#63)
* Base script: print warning/debug messages to stderr (sdsc#60)
* Base script: improve sentence semgmentation

* Documentation: add version to manpage (sdsc#8)

* Packaging: bookmarklet is not shipped (sdsc#96)
* Packaging: adapted packaging to new source structure as a Python module

* Linting: Use PEP8 (sdsc#17)
* Tests: create a Integration Test Suite (sdsc#4)
* Tests:--checkpatterns might be better suited to a test enhancement (sdsc#74)
* Tests: Validate the XML files in src/sdsc/xsl-checks (sdsc#85)
* Tests: Avoid building libxml each time on Travis (sdsc#77)
* Tests: check whether command line options work (sdsc#67)
* Tests: Do not output "pytest.fail()" lines (sdsc#65)
* Project infrastructure: Python packaging with setup.py (sdsc#13)
* Project infrastructure: use a script for updating the version number (related: sdsc#8)
* Project infrastructure: restructure source tree using cookiecutter-pylibrary (sdsc#2)

