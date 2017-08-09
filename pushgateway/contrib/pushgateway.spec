%define distnum %{expand:%%(/usr/lib/rpm/redhat/dist.sh --distnum)}
%define disttype %{expand:%%(/usr/lib/rpm/redhat/dist.sh --disttype)}

%define _unpackaged_files_terminate_build 0
%define debug_package %{nil}
%define use_systemd (0%{?fedora} && 0%{?fedora} >= 18) || (0%{?rhel} && 0%{?rhel} >= 7) || (0%{?suse_version} && 0%{?suse_version} >=1210)

%define debug_package %{nil}

%define release 1.ptin.%{disttype}%{distnum}

Name:		pushgateway
Version:	%{version}
Release:	%{release}
Summary:	The pushgateway handles alerts sent by client applications such as the Prometheus server.
Group:		System Environment/Daemons
License:	See the LICENSE file at github.
URL:		https://github.com/prometheus/pushgateway
Source0:	https://github.com/prometheus/pushgateway/releases/download/%{version}/pushgateway-%{version}.linux-amd64.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-root
Requires(pre):  /usr/sbin/useradd
%if %{use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif
AutoReqProv:	No

%description

The pushgateway handles alerts sent by client applications such as the Prometheus server. 
It takes care of deduplicating, grouping, and routing them to the correct receiver integration such as email, PagerDuty, or OpsGenie. 
It also takes care of silencing and inhibition of alerts.


%prep
%setup -q -n %{name}-%{version}.linux-amd64

%build
echo

%install
mkdir -vp $RPM_BUILD_ROOT/var/log/prometheus/
mkdir -vp $RPM_BUILD_ROOT/var/run/prometheus
mkdir -vp $RPM_BUILD_ROOT/var/lib/prometheus
mkdir -vp $RPM_BUILD_ROOT/usr/bin
mkdir -vp $RPM_BUILD_ROOT/etc/prometheus
%if %{use_systemd}
mkdir -vp $RPM_BUILD_ROOT/usr/lib/systemd/system
install -m 755 contrib/pushgateway.service $RPM_BUILD_ROOT/usr/lib/systemd/system/pushgateway.service
%else
mkdir -vp $RPM_BUILD_ROOT/etc/init.d
mkdir -vp $RPM_BUILD_ROOT/etc/sysconfig
install -m 755 contrib/pushgateway.init $RPM_BUILD_ROOT/etc/init.d/pushgateway
install -m 644 contrib/pushgateway.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/pushgateway
%endif
install -m 755 pushgateway $RPM_BUILD_ROOT/usr/bin/pushgateway

%clean

%pre
getent group prometheus >/dev/null || groupadd -r prometheus
getent passwd prometheus >/dev/null || \
  useradd -r -g prometheus -s /sbin/nologin \
    -d $RPM_BUILD_ROOT/var/lib/prometheus/ -c "prometheus Daemons" prometheus
exit 0

%post
chgrp prometheus /var/run/prometheus
chmod 774 /var/run/prometheus
chown prometheus:prometheus /var/log/prometheus
chmod 744 /var/log/prometheus

%files
%defattr(-,root,root,-)
/usr/bin/pushgateway
%if %{use_systemd}
/usr/lib/systemd/system/pushgateway.service
%else
/etc/init.d/pushgateway
%config(noreplace) /etc/sysconfig/pushgateway
%endif
