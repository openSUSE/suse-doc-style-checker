#
# spec file for package suse-doc-style-checker
#
# Copyright (c) 2014 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Change this file in the Git repository at
# www.gitorious.org/style-checker/style-checker, not in the Build Service

%define aliasname sdsc

Name:           suse-doc-style-checker
Version:        2014~02.2.rc2
Release:        0
Url:            http://www.gitorious.org/style-checker/style-checker
Summary:        Style Checker for SUSE Documentation
License:        LGPL-2.1+
Group:          Productivity/Publishing/XML
Source:         %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

BuildRequires:  docbook-xsl-stylesheets
BuildRequires:  libxslt-tools
BuildRequires:  python3-devel
BuildRequires:  python3-lxml
Requires:       python3
Requires:       python3-lxml
Recommends:     intel-clear-sans-fonts


%description
A command that checks documentation for compliance with the SUSE
Style Guide. Among other things, it checks for terminology, duplicated
words, long sentences, and lone subsections.

%prep
%setup -q -n %{name}-%{version}

%build
python3 setup.py build
# Create man pages
DB=/usr/share/xml/docbook/stylesheet/nwalsh/current/
(cd man;
xsltproc $DB/manpages/docbook.xsl suse-doc-style-checker.xml
)

%install
./setup.py install --prefix=%{_prefix} --root=%{buildroot} --install-data=%_datadir/%{name}
# Install man pages:
mkdir -p %{buildroot}%{_mandir}/man1 %{buildroot}%_bindir
install -m644 man/%{aliasname}.1  %{buildroot}%{_mandir}/man1

(cd %{buildroot}%_datadir/%{name}/source/;
ln -sr %{aliasname} %{buildroot}%_bindir/%{aliasname};
ln -sr %{aliasname} %{buildroot}%_bindir/%{name}
)
(cd  %{buildroot}%{_mandir}/man1;
ln -sr %{aliasname}.1 %{name}.1
)

%files
%defattr(-,root,root,-)
# You may have to add additional files here (documentation and binaries mostly)
%doc LICENSE
%{python3_sitelib}/*
%_bindir/%{name}
%_bindir/%{aliasname}
%dir %_datadir/%{name}
%_datadir/%{name}
%{_mandir}/man1/%{name}.1%{ext_man}
%{_mandir}/man1/%{aliasname}.1%{ext_man}

%changelog