%define distnum %{expand:%%(/usr/lib/rpm/redhat/dist.sh --distnum)}
%define disttype %{expand:%%(/usr/lib/rpm/redhat/dist.sh --disttype)}

%define _unpackaged_files_terminate_build 0
%define debug_package %{nil}
%define use_systemd (0%{?fedora} && 0%{?fedora} >= 18) || (0%{?rhel} && 0%{?rhel} >= 7) || (0%{?suse_version} && 0%{?suse_version} >=1210)

%define release 1.ptin.%{disttype}%{distnum}

Name:		node-exporter
Version:        %{version}
Release:        %{release}
Summary:	Prometheus exporter for machine metrics, written in Go with pluggable metric collectors.
Group:		System Environment/Daemons
License:	See the LICENSE file at github.
URL:		https://github.com/prometheus/node_exporter
Source0:        https://github.com/prometheus/node_exporter/releases/download/%{version}/node_exporter-%{version}.linux-amd64.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-root
Requires(pre):  /usr/sbin/useradd
%if %{use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif
AutoReqProv:    No

%description

Prometheus exporter for machine metrics, written in Go with pluggable metric collectors.

%prep
%setup -q -n node_exporter-%{version}.linux-amd64

%build
echo

%install
mkdir -vp $RPM_BUILD_ROOT/var/run/prometheus
mkdir -vp $RPM_BUILD_ROOT/var/lib/prometheus
mkdir -vp $RPM_BUILD_ROOT/usr/bin
mkdir -vp $RPM_BUILD_ROOT/opt/prometheus
%if %{use_systemd}
mkdir -vp $RPM_BUILD_ROOT/usr/lib/systemd/system
install -m 755 contrib/node_exporter.service $RPM_BUILD_ROOT/usr/lib/systemd/system/node_exporter.service
%else
mkdir -vp $RPM_BUILD_ROOT/etc/init.d
mkdir -vp $RPM_BUILD_ROOT/etc/sysconfig
install -m 644 contrib/node_exporter.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/node_exporter
install -m 755 contrib/node_exporter.init $RPM_BUILD_ROOT/etc/init.d/node_exporter
%endif
install -m 755 node_exporter $RPM_BUILD_ROOT/usr/bin/node_exporter

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
chown prometheus:prometheus /opt/prometheus
chmod 744 /opt/prometheus
sudo service node_exporter start

%files
%defattr(-,root,root,-)
/usr/bin/node_exporter
/var/run/prometheus
/opt/prometheus
%if %{use_systemd}
/usr/lib/systemd/system/node_exporter.service
%else
%config(noreplace) /etc/sysconfig/node_exporter
/etc/init.d/node_exporter
%endif
