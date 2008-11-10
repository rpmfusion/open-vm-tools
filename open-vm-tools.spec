%define builddate 2008.10.10
%define buildver 123053

Name:      open-vm-tools
Version:   0.0.0.%{buildver}
Release:   9%{?dist}
Summary:   VMware Guest OS Tools
Group:     Applications/System
License:   LGPLv2
URL:       http://open-vm-tools.sourceforge.net/
Source0:   http://downloads.sourceforge.net/%{name}/%{name}-%{builddate}-%{buildver}.tar.gz
Source1:   %{name}-guestd.init
Source2:   %{name}-sysconfig.mouse
Source3:   vmware-toolbox.desktop
Source4:   %{name}-modprobe.vmnics
Patch0:    %{name}-123053-desktop.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

ExclusiveArch: i386 x86_64

BuildRequires: gtk2-devel
BuildRequires: libXtst-devel
BuildRequires: libdnet-devel
BuildRequires: procps
BuildRequires: libdnet-devel
BuildRequires: libicu-devel
BuildRequires: desktop-file-utils

Requires:  open-vm-tools-kmod >= %{version}
Obsoletes: open-vm-tools-kmod < %{version}
Provides:  open-vm-tools-kmod-common = %{version}


%description
Open-vm-tools are the open source implementation of VMware Tools. They
are a set of guest operating system virtualization components that
enhance performance and user experience of VMWare virtual
machines. This package contains the user-space programs and libraries
of open-vm-tools.

%package        devel
Summary:        Development package for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description    devel
Open-vm-tools are the open source implementation of VMware Tools. They
are a set of guest operating system virtualization components that
enhance performance and user experience of VMWare virtual
machines. This package contains the header files and symlinks to 
libraries.


%prep
%setup -q -n open-vm-tools-%{builddate}-%{buildver}
%patch0 -p1 -b .desktop
# Fix some permissions and formats
chmod -x NEWS README ChangeLog AUTHORS COPYING
sed -i 's/\r//' README


%build
%configure \
        --disable-static \
        --disable-dependency-tracking \
        --disable-unity \
        --without-kernel-modules \
        --without-root-privileges

make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -type f -name "*.la" -exec rm -f {} ';'

# Install vmware-guestd init script
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
install -m 0755 %{SOURCE1} $RPM_BUILD_ROOT/etc/init.d/vmware-guestd

# GPM vmmouse support
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/mouse

# Move mount.vmhgfs to correct location in /sbin
mkdir -p $RPM_BUILD_ROOT/sbin
mv $RPM_BUILD_ROOT%{_sbindir}/mount.* $RPM_BUILD_ROOT/sbin

# Install VMCI sockets header file
mkdir -p $RPM_BUILD_ROOT%{_includedir}
install -m 0644 modules/linux/vsock/linux/vmci_sockets.h $RPM_BUILD_ROOT%{_includedir}

# Move vmware-user desktop into autostart directory
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart
mv $RPM_BUILD_ROOT%{_datadir}/applications/vmware-user.desktop $RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/

# Install desktop file and icon for toolbox
mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps
install -m 0644 toolbox/bigIcon.xpm $RPM_BUILD_ROOT%{_datadir}/pixmaps/vmware-toolbox.xpm
desktop-file-install --dir $RPM_BUILD_ROOT%{_datadir}/applications %{SOURCE3}

# Setup module-init-tools file for vmxnet
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d
install -m 0644 %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/vmnics


%clean
rm -rf $RPM_BUILD_ROOT


%post
# Setup guestd on initial install
/sbin/ldconfig
[ $1 -lt 2 ] && /sbin/chkconfig vmware-guestd on ||:
update-desktop-database %{_datadir}/applications > /dev/null 2>&1 || :


%postun
update-desktop-database %{_datadir}/applications > /dev/null 2>&1 || :
/sbin/ldconfig


%preun
# Remove on uninstall
if [ "$1" = 0 ]
then
  /sbin/service vmware-guestd stop > /dev/null 2>&1 || :
  /sbin/chkconfig --del vmware-guestd ||:
fi


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING ChangeLog NEWS README
%{_bindir}/vmware*
%{_sbindir}/vmware*
%{_datadir}/applications/*.desktop
%{_sysconfdir}/xdg/autostart/*.desktop
%{_datadir}/pixmaps/*.xpm
%{_libdir}/*.so.*
%{_sysconfdir}/init.d/*
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/pam.d/vmware-guestd*
%dir %{_sysconfdir}/vmware-tools
%{_sysconfdir}/vmware-tools/poweroff-vm-default
%{_sysconfdir}/vmware-tools/poweron-vm-default
%{_sysconfdir}/vmware-tools/resume-vm-default
%{_sysconfdir}/vmware-tools/suspend-vm-default
%{_sysconfdir}/vmware-tools/vm-support
%config(noreplace) %{_sysconfdir}/vmware-tools/tools.conf
%config(noreplace) %{_sysconfdir}/sysconfig/mouse
%config(noreplace) %{_sysconfdir}/modprobe.d/*
%attr(4755,root,root) /sbin/mount.vmhgfs
%attr(4755,root,root) %{_bindir}/vmware-user-suid-wrapper


%files devel
%defattr(-,root,root,-)
%{_includedir}/*.h
%{_libdir}/*.so


%changelog
* Mon Nov 10 2008 Denis Leroy <denis@poolshark.org> - 0.0.0.123053-9
- Some more cleanups

* Fri Oct 31 2008 Denis Leroy <denis@poolshark.org> - 0.0.0.123053-8
- Added toolbox icon

* Tue Oct 28 2008 Denis Leroy <denis@poolshark.org> - 0.0.0.123053-7
- Only export vmci_sockets.h file

* Mon Oct 27 2008 Orcan Ogetbil <orcan [AT] yahoo [DOT] com> 0.0.0.123053-6
- Bugfix: Doesn't build for x86_64.
- Added a devel package containing the header and .so files.
- The shell scripts in %%{_sysconfdir}/vmware-tools/ are now marked non-%%config.
- Minor SPEC file improvements.

* Mon Oct 27 2008 Denis Leroy <denis@poolshark.org> - 0.0.0.123053-5
- Fixed desktop-file-utils reqs

* Sun Oct 26 2008 Denis Leroy <denis@poolshark.org> - 0.0.0.123053-4
- Move drag'n'drop directory management to init script
- Added icon to toolbox desktop entry
- Some rpmlint cleanups

* Tue Oct 21 2008 Denis Leroy <denis@poolshark.org> - 0.0.0.123053-2
- Changed versioning
- Added patches and extra config files as sources

* Wed Oct 15 2008 Denis Leroy <denis@poolshark.org> - 0-1.2008.10.10
- First draft, based on dkms-based spec
