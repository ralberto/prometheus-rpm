%define distnum %{expand:%%(/usr/lib/rpm/redhat/dist.sh --distnum)}
%define disttype %{expand:%%(/usr/lib/rpm/redhat/dist.sh --disttype)}

%define _unpackaged_files_terminate_build 0
%define debug_package %{nil}
%define use_systemd (0%{?fedora} && 0%{?fedora} >= 18) || (0%{?rhel} && 0%{?rhel} >= 7) || (0%{?suse_version} && 0%{?suse_version} >=1210)

%define release 1.ptin.%{disttype}%{distnum}

Name:		alertmanager
Version:	%{version}
Release:  %{release}
Summary:	The Alertmanager handles alerts sent by client applications such as the Prometheus server.
Group:		System Environment/Daemons
License:	See the LICENSE file at github.
URL:		https://github.com/prometheus/alertmanager
Source0:	https://github.com/prometheus/alertmanager/releases/download/%{version}/alertmanager-%{version}.linux-amd64.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-root
Requires(pre):  /usr/sbin/useradd

%if %{use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif
AutoReqProv:    No

%description

The Alertmanager handles alerts sent by client applications such as the Prometheus server.
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
mkdir -vp $RPM_BUILD_ROOT/etc/prometheus/alertmanager
%if  %{use_systemd}
mkdir -vp $RPM_BUILD_ROOT/usr/lib/systemd/system
install -m 755 contrib/alertmanager.service $RPM_BUILD_ROOT/usr/lib/systemd/system/alertmanager.service
%else
mkdir -vp $RPM_BUILD_ROOT/etc/init.d
mkdir -vp $RPM_BUILD_ROOT/etc/sysconfig
install -m 755 contrib/alertmanager.init $RPM_BUILD_ROOT/etc/init.d/alertmanager
install -m 644 contrib/alertmanager.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/alertmanager
%endif
install -m 644 simple.yml $RPM_BUILD_ROOT/etc/prometheus/alertmanager/alertmanager.yaml
install -m 755 alertmanager $RPM_BUILD_ROOT/usr/bin/alertmanager

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
/usr/bin/alertmanager
%config(noreplace) /etc/prometheus/alertmanager/alertmanager.yaml
%if %{use_systemd}
/usr/lib/systemd/system/alertmanager.service
%else
/etc/init.d/alertmanager
%config(noreplace) /etc/sysconfig/alertmanager
%endif
