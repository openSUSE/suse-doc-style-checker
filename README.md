# SUSE Documentation Style Checker

**This repository is archieved. Use vscode-suse-vale-styleguide and suse-vscode-doc.**

With its little mind tries very hard to check whether documentation is compliant with the
[SUSE Documentation Style Guide](https://github.com/SUSE/doc-styleguide).

Releases are usually aligned with releases of the Style Guide.


## Usage

* To use SDSC from this Git repository, set up a
  [Python 3 Virtual Environment](https://github.com/openSUSE/suse-doc-style-checker/wiki/Initializing-Python3-Virtual-Environment)

* On openSUSE systems, you can install the RPM version of SDSC from
  [the Documentation:Tools project](https://build.opensuse.org/project/show/Documentation:Tools)


## Testing the branch
1. Create a new Python environment with the command: <pre>python3 -m venv .env</pre>
2. Activate the environment with: <pre>source .env/bin/activate</pre>
3. Update the environment: <pre>pip3 install --upgrade pip setuptools</pre>
4. "Install" the SUSE stylechecker inside the environment with: <pre>./setup.py develop</pre>
5. Use any existing XML file for testing: <pre>sdsc <XML_FILE></pre>
6. To compare with the system stylechecker, use the absolute path to the script like: <pre>/usr/bin/sdsc <XML_FILE></pre>

To get rid of the environment in your GitHub repo, execute these final steps:
1. Deactivate the environment first: <pre>deactivate</pre>
2. Remove the <strong>.env</strong> folder with: <pre>rm -rf .env</pre>


## Lucky Charms

[![Build Status](https://travis-ci.org/openSUSE/suse-doc-style-checker.svg?branch=main)](https://travis-ci.org/openSUSE/suse-doc-style-checker)
[![Coverage Status](https://coveralls.io/repos/github/openSUSE/suse-doc-style-checker/badge.svg?branch=main)](https://coveralls.io/github/openSUSE/suse-doc-style-checker?branch=main)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/openSUSE/suse-doc-style-checker/badges/quality-score.png?b=main)](https://scrutinizer-ci.com/g/openSUSE/suse-doc-style-checker/?branch=main)
