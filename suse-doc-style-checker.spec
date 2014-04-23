#
# spec file for package stylechecker
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

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%define aliasname sdsc

Name:           suse-doc-style-checker
Version:        0.0.99
Release:        0
Url:            http://www.gitorious.org/style-checker/style-checker
Summary:        Style Checker for SUSE Documentation
License:        MIT
Group:          Productivity/Publishing/XML
Source0:        http://pypi.python.org/packages/source/d/doit/%{name}-%{version}.tar.gz
#Source1:        %%{name}.xml
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
BuildRequires:  docbook-xsl-stylesheets
BuildRequires:  libxslt-tools
BuildRequires:  python3-devel
BuildRequires:  python3-lxml
# Requires:       python(abi) = %{py3_ver}
Requires:       python3-lxml
Recommends:     intel-clear-sans-fonts


%description
TBD

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
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot} --install-data=%_datadir/%{name}
# Install man pages:
mkdir -p %{buildroot}%{_mandir}/man1 %{buildroot}%_bindir
install -m644 man/%{name}.1  %{buildroot}%{_mandir}/man1

(cd %{buildroot}%_datadir/%{name}/source/;
 ln -sr %{aliasname} %{buildroot}%_bindir
)
(cd %{buildroot}%_bindir ;
 ln -sr %{aliasname} %{name}
)
(cd  %{buildroot}%{_mandir}/man1;
ln -sr %{name}.1 %{aliasname}.1
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
