%define builddate 2009.07.22
%define buildver 179896

Name:      open-vm-tools
Version:   0.0.0.%{buildver}
Release:   1%{?dist}
Summary:   VMware Guest OS Tools
Group:     Applications/System
License:   LGPLv2
URL:       http://open-vm-tools.sourceforge.net/
Source0:   http://downloads.sourceforge.net/%{name}/%{name}-%{builddate}-%{buildver}.tar.gz
Source1:   %{name}-guestd.init
Source2:   %{name}-sysconfig.mouse
Source3:   vmware-toolbox.desktop
Source4:   %{name}-modprobe.vmnics
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

ExclusiveArch: i586 x86_64

BuildRequires: gtk2-devel
BuildRequires: gtkmm24-devel
BuildRequires: libXtst-devel
BuildRequires: libdnet-devel
BuildRequires: pam-devel
BuildRequires: procps
BuildRequires: libdnet-devel
BuildRequires: libicu-devel
BuildRequires: desktop-file-utils
BuildRequires: uriparser-devel
BuildRequires: libnotify-devel
BuildRequires: libXScrnSaver-devel
BuildRequires: doxygen graphviz

Requires:  open-vm-tools-kmod >= %{version}
Obsoletes: open-vm-tools-kmod < %{version}
Provides:  open-vm-tools-kmod-common = %{version}


%description
Open-vm-tools are the open source implementation of VMware Tools. They
are a set of guest operating system virtualization components that
enhance performance and user experience of VMWare virtual
machines. This package contains the user-space programs and libraries
of open-vm-tools.

%package   libs
Summary:   Libraries for %{name}
Group:     System Environment/Libraries


%description libs
The %{name}-libs package contains the runtime shared libraries for
%{name}.


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
# Fix some permissions and formats
chmod -x NEWS README ChangeLog AUTHORS COPYING
sed -i 's/\r//' README


%build
%configure \
        --disable-static \
        --enable-docs \
        --disable-dependency-tracking \
        --without-kernel-modules \
        --without-root-privileges \
        --with-gtkmm

# Disable use of rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -type f -name "*.la" -exec rm -f {} ';'

# Install vmtoolsd init script
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
install -m 0755 %{SOURCE1} $RPM_BUILD_ROOT/etc/init.d/vmtoolsd

# GPM vmmouse support
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/mouse

# Move mount.vmhgfs to correct location in /sbin
mkdir -p $RPM_BUILD_ROOT/sbin
mv $RPM_BUILD_ROOT%{_sbindir}/mount.* $RPM_BUILD_ROOT/sbin

# Install VMCI sockets header file
mkdir -p $RPM_BUILD_ROOT%{_includedir}
install -m 0644 lib/include/vmci_sockets.h $RPM_BUILD_ROOT%{_includedir}

# Move vmware-user desktop into autostart directory
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart
mv $RPM_BUILD_ROOT%{_datadir}/applications/vmware-user.desktop $RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/

# Install desktop file and icon for toolbox
mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps
install -m 0644 toolbox/bigIcon.xpm $RPM_BUILD_ROOT%{_datadir}/pixmaps/vmware-toolbox.xpm
desktop-file-install --dir $RPM_BUILD_ROOT%{_datadir}/applications %{SOURCE3}

# Setup module-init-tools file for vmxnet
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d
install -m 0644 %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/vmnics.conf

# Set suid bit on vmware-user suid wrapper
chmod +s  $RPM_BUILD_ROOT%{_bindir}/vmware-user-suid-wrapper


%clean
rm -rf $RPM_BUILD_ROOT


%post
# Setup guestd on initial install
/sbin/ldconfig
[ $1 -lt 2 ] && /sbin/chkconfig vmtoolsd on ||:
update-desktop-database %{_datadir}/applications > /dev/null 2>&1 || :


%postun
update-desktop-database %{_datadir}/applications > /dev/null 2>&1 || :
/sbin/ldconfig


%preun
# Remove on uninstall
if [ "$1" = 0 ]
then
  /sbin/service vmtoolsd stop > /dev/null 2>&1 || :
  /sbin/chkconfig --del vmtoolsd ||:
fi


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING ChangeLog NEWS README
%doc %{_docdir}/open-vm-tools
%{_bindir}/vm*
%{_datadir}/applications/*.desktop
%{_sysconfdir}/xdg/autostart/*.desktop
%{_datadir}/pixmaps/*.xpm
%{_datadir}/open-vm-tools
%{_sysconfdir}/init.d/*
%{_sysconfdir}/vmware-tools
%config(noreplace) %{_sysconfdir}/pam.d/*
%config(noreplace) %{_sysconfdir}/sysconfig/mouse
%config(noreplace) %{_sysconfdir}/modprobe.d/*
%attr(4755,root,root) /sbin/mount.vmhgfs


%files libs
%defattr(-,root,root,-)
%{_libdir}/*.so.*
%{_libdir}/open-vm-tools


%files devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc


%changelog
* Fri Aug 14 2009 Denis Leroy <denis@poolshark.org> - 0.0.0.179896-1
- Update to upstream build 179896
- Some new content in devel package
- Plugin path patch upstreamed

* Sat Jul  4 2009 Denis Leroy <denis@poolshark.org> - 0.0.0.172495-1
- Update to upstream build 172495
- Split libs subpackage for multilib friendliness
- Added pam-devel BR
- Switch to vmtoolsd for vmsvc, updated init file
- Added patch to fix default vmtoolsd plugin path

* Fri Apr  3 2009 Denis Leroy <denis@poolshark.org> - 0.0.0.154848-3
- Fixing ExclusiveArch

* Sat Mar 28 2009 Denis Leroy <denis@poolshark.org> - 0.0.0.154848-2
- Updated arches for F-11

* Mon Mar 23 2009  <denis@poolshark.org> - 0.0.0.154848-1
- Update to upstream build 154848
- Some renames, config dir simplification
- Added plugin directory
- Fixed rpath issue

* Wed Jan 28 2009 Denis Leroy <denis@poolshark.org> - 0.0.0.142982-1
- Update to upstream build 142982
- Bug fixes, support for more recent kernels

* Sat Jan 10 2009 Denis Leroy <denis@poolshark.org> - 0.0.0.137496-1
- Update to upstream build 137496

* Thu Dec 18 2008 Denis Leroy <denis@poolshark.org> - 0.0.0.130226-1
- Update to upstream 130226
- Desktop patch upstreamed

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
