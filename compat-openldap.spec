Summary: OpenLDAP compatibility shared libraries
Name: compat-openldap
Epoch: 1
Version: 2.3.43
Release: 2%{?dist}
License: OpenLDAP
Group: System Environment/Libraries
URL: http://www.openldap.org/

Source0: ftp://ftp.OpenLDAP.org/pub/OpenLDAP/openldap-release/openldap-%{version}.tgz

Patch0: openldap-2.0.11-ldaprc.patch
Patch1: openldap-2.3.19-gethostbyXXXX_r.patch
Patch2: openldap-2.2.13-setugid.patch
Patch3: openldap-2.3.11-nosql.patch
Patch4: openldap-2.3.27-config-sasl-options.patch
Patch5: openldap-2.3.42-network-timeout.patch
Patch6: openldap-2.3.43-chase-referral.patch
Patch7: openldap-2.3.43-tls-null-char.patch
Patch8: openldap-2.3.43-compat-macros.patch

BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires: glibc-devel, cyrus-sasl-devel >= 2.1, openssl-devel
# require current OpenLDAP libraries to have /etc/openldap/ldap.conf
Requires: openldap >= 2.4

%description
OpenLDAP is an open source suite of LDAP (Lightweight Directory Access
Protocol) applications and development tools. The compat-openldap package
includes older versions of the OpenLDAP shared libraries which may be
required by some applications.


%prep
%setup -q -n openldap-%{version}

%patch0 -p1 -b .ldaprc
%patch1 -p1 -b .gethostbyXXXX_r
%patch2 -p1 -b .setugid
%patch3 -p1 -b .nosql
%patch4 -p1 -b .config-sasl-options
%patch5 -p1 -b .network-timeout
%patch6 -p1 -b .chase-referral
%patch7 -p1 -b .tls-null-char
%patch8 -p1 -b .compat-macros


%build
%ifarch ia64
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -O0"
%endif

export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -D_REENTRANT -fPIC -D_GNU_SOURCE"

%configure \
	--disable-slapd --disable-slurpd \
	--with-threads=posix --enable-static --enable-shared --enable-dynamic \
	--enable-local --with-tls --with-cyrus-sasl --without-kerberos

# get rid of rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT

pushd libraries
	make install DESTDIR=$RPM_BUILD_ROOT

	# drop static libraries
	rm -f $RPM_BUILD_ROOT/%{_libdir}/*.{a,la}

	# two sets of libraries share the soname, compat is not default
	rm -f $RPM_BUILD_ROOT/%{_libdir}/*.so

	# fix permissions to correctly generate debuginfo
	chmod 0755 $RPM_BUILD_ROOT/%{_libdir}/*
popd

# remove all configuration files
rm -rf $RPM_BUILD_ROOT/etc


%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc ANNOUNCEMENT
%doc COPYRIGHT
%doc LICENSE
%attr(0755,root,root) %{_libdir}/liblber-2.3.so.*
%attr(0755,root,root) %{_libdir}/libldap-2.3.so.*
%attr(0755,root,root) %{_libdir}/libldap_r-2.3.so.*


%changelog
* Mon Nov 22 2010 Jan Vcelak <jvcelak@redhat.com> 1:2.3.43-2
- run ldconfig in post and postun
- remove rpath

* Thu Nov 11 2010 Jan Vcelak <jvcelak@redhat.com> 1:2.3.43-1
- split from openldap package
