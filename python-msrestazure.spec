%if 0%{?fedora}
%global _with_python3 1
# Tests disabled on EPEL because of missing dependencies
%global _with_tests 1
%endif

%if 0%{?rhel}
%global py2_prefix python
%else
%global py2_prefix python2
%endif

%global srcname msrestazure

%global common_summary AutoRest swagger generator Python client runtime (Azure-specific module)
%global common_description %{common_summary}.

# python-keyring
%global keyring_version    5.7.1
%global bundled_lib_dir    bundled
%global keyring_dir        %{bundled_lib_dir}/keyring

%global adal_min_version 0.6.0
%global msrest_min_version 0.5.4

Name:           python-%{srcname}
Version:        0.5.1
Release:        0%{?dist}.1
Summary:        %{common_summary}

Group:          System Environment/Libraries
License:        MIT and Python
URL:            https://github.com/Azure/msrestazure-for-python/
Source0:        https://github.com/Azure/msrestazure-for-python/archive/v%{version}/%{srcname}-%{version}.tar.gz
Source1:        https://pypi.io/packages/source/k/keyring/keyring-%{keyring_version}.tar.gz

BuildRequires:  python-setuptools
BuildRequires:  python-devel

Requires:       %{py2_prefix}-adal >= %{adal_min_version}
Requires:       %{py2_prefix}-msrest >= %{msrest_min_version}

Provides:       bundled(python-keyring) = %{keyring_version}

%if 0%{?_with_python3}
BuildRequires:  python3-devel
%endif
%if 0%{?_with_tests}
BuildRequires:  %{py2_prefix}-adal >= %{adal_min_version}
BuildRequires:  %{py2_prefix}-certifi
BuildRequires:  python-httpretty
BuildRequires:  %{py2_prefix}-keyring
BuildRequires:  %{py2_prefix}-msrest >= %{msrest_min_version}
%if 0%{?_with_python3}
BuildRequires:  python3-adal >= %{adal_min_version}
BuildRequires:  python3-certifi
BuildRequires:  python3-httpretty
BuildRequires:  python3-keyring
BuildRequires:  python3-msrest >= %{msrest_min_version}
%endif
%endif
BuildArch:      noarch

%description
%{common_description}


%if 0%{?_with_python3}
%package -n python3-%{srcname}
Summary:        %{common_summary}
Requires:       python3-adal >= %{adal_min_version}
Requires:       python3-keyring
Requires:       python3-msrest >= %{msrest_min_version}
%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname}
%{common_description}
%endif


%prep
%autosetup -n %{srcname}-for-python-%{version}

# python-keyring bundle
mkdir -p %{bundled_lib_dir}
tar -xzf %SOURCE1 -C %{bundled_lib_dir}
mv %{bundled_lib_dir}/keyring-%{keyring_version} %{keyring_dir}
cp %{keyring_dir}/CHANGES.rst keyring_CHANGES.rst
cp %{keyring_dir}/README.rst keyring_README.rst
sed -i "/        'setuptools_scm>=1.9',/d" %{keyring_dir}/setup.py

pushd %{keyring_dir}
rm -frv keyring.egg-info
# Drop redundant shebangs.
sed -i '1{\@^#!/usr/bin/env python@d}' keyring/cli.py
# Drop slags from upstream of using his own versioning system.
sed -i -e "\@use_vcs_version@s/^.*$/\tversion = \"%{keyring_version}\",/g" \
       -e {/\'hgtools\'/d} setup.py
popd
# append bundled-directory to search path
sed -i "/^    import keyring/i\ \ \ \ import sys\n\ \ \ \ sys.path.insert(0, '%{_libdir}/fence-agents/bundled')" msrestazure/azure_active_directory.py

%build
%py2_build
%{?_with_python3:%py3_build}
# python-keyring bundle
pushd %{keyring_dir}
%{__python2} setup.py build
popd


%install
%py2_install
%{?_with_python3:%py3_install}
# python-keyring bundle
pushd %{keyring_dir}
%{__python2} setup.py install -O1 --skip-build --root %{buildroot} --install-lib %{_libdir}/fence-agents/bundled
popd


%check
%if 0%{?_with_tests}
%{__python2} setup.py test
%{?_with_python3:%{__python3} setup.py test}
%endif


%files -n python-%{srcname}

%doc README.rst keyring_CHANGES.rst keyring_README.rst
%license LICENSE.md
%{python2_sitelib}/*
%{_libdir}/fence-agents/bundled
%exclude %{_bindir}/keyring


%if 0%{?_with_python3}
%files -n python3-%{srcname}
%doc README.rst
%license LICENSE.md
%{python3_sitelib}/*
%endif


%changelog
* Thu May 16 2019 Oyvind Albrigtsen <oalbrigt@redhat.com> - 0.5.1-0.1
- Update to 0.5.1
  Resolves: rhbz#1709114

* Thu Jan 25 2018 Oyvind Albrigtsen <oalbrigt@redhat.com> - 0.4.16-3
- Bundle python-keyring
- Append python-keyring bundled directory to search path where needed

  Resolves: rhbz#1511228

* Fri Nov 10 2017 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.16-1
- Update to 0.4.16

* Tue Oct 17 2017 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.15-2
- Update build patch for EL7

* Tue Oct 17 2017 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.15-1
- Update to 0.4.15

* Fri Oct 06 2017 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.14-1
- Update to 0.4.14

* Wed Aug 30 2017 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.13-1
- Update to 0.4.13
- Use python2- prefix for Fedora dependencies if possible

* Fri Jul 21 2017 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.11-1
- Update to 0.4.11

* Sat Jun 10 2017 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.8-1
- Update to 0.4.8

* Thu Jan 26 2017 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.7-1
- Update to 0.4.7
- Enable check tests, now available in this version

* Wed Dec 21 2016 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.6-1
- Update to 0.4.6

* Thu Oct 20 2016 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.4-1
- Update to 0.4.4
- Remove checks since there's no test

* Tue Sep 27 2016 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.3-1
- Update to 0.4.3

* Fri Jun 24 2016 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.1-1
- Update to 0.4.1

* Thu May 26 2016 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.4.0-1
- Update to 0.4.0

* Sun May 01 2016 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.3.0-1
- Update to 0.3.0

* Fri Apr 01 2016 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.2.1-1
- Update to 0.2.1

* Wed Mar 23 2016 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.1.2-1
- Update to 0.1.3

* Sat Mar 05 2016 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.1.1-1
- Update to 0.1.1

* Wed Mar 02 2016 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.0.2-1
- Update to 0.0.2

* Sun Feb 28 2016 Mohamed El Morabity <melmorabity@fedoraproject.org> - 0.0.1-1
- Initial RPM release
