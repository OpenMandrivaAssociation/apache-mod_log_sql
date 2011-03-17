#Module-Specific definitions
%define mod_name mod_log_sql
%define mod_conf A25_%{mod_name}.conf
%define mod_so %{mod_name}.so

%define apache_version 2.0.55

Summary:	Logs to MySQL
Name:		apache-%{mod_name}
Version:	1.101
Release:	%mkrel 14
Group:		System/Servers
License:	Apache License
URL:		http://www.outoforder.cc/projects/apache/mod_log_sql/
Source0: 	%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}
BuildRequires:	mysql-devel
#BuildRequires:	openssl-devel
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.0.54
Requires(pre):	apache >= %{apache_version}
Requires:	apache-conf >= 2.0.54
Requires:	apache >= %{apache_version}
BuildRequires:	apache-devel >= %{apache_version}
BuildRequires:	file
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_log_sql offers Apache administrators the ability to log accesses
to a MySQL database. This capability can replace or coexist with Apache's
regular text-file logging mechanisms. mod_log_sql is production-ready
and is known to work with high volume webservers and webserver clusters
supporting over 100,000 hits per day.

%prep

%setup -q -n mod_log_sql-%{version}

cp %{SOURCE1} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

%configure2_5x --localstatedir=/var/lib \
    --with-apxs=%{_sbindir}/apxs \
    --with-mysql=%{_prefix}

#    --enable-ssl \
#    --with-ssl-inc=%{_includedir}/openssl \
#    --with-db-inc=%{_includedir}/db1

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/mod_log_sql.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0755 .libs/mod_log_sql_mysql.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}%{_var}/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}%{_var}/www/html/addon-modules/%{name}-%{version}

cp contrib/README README.contrib

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS CHANGELOG INSTALL LICENSE TODO README* docs/*.html contrib/*.sql
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_log_sql.so
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_log_sql_mysql.so
%{_var}/www/html/addon-modules/*


