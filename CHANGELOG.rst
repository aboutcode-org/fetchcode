Changelog
=========

v0.5.2
------
- Update link references of ownership from nexB to aboutcode-org


v0.5.1
-------
- Use authenticated requests for GitHub REST API calls


v0.5.0
-------
- FetchCode now supports retrieving package info for following generic packages:
    * pkg:generic/linux
    * pkg:generic/mtd-utils
    * pkg:generic/barebox
    * pkg:generic/e2fsprogs
    * pkg:generic/udhcp
    * pkg:generic/miniupnpc
    * pkg:generic/miniupnpd
    * pkg:generic/minissdpd
    * pkg:generic/erofs-utils
    * pkg:openssl/openssl

- FetchCode also supports retrieving package info for packages hosted on GitHub specifically.
    * pkg:github/avahi/avahi
    * pkg:github/bestouff/genext2fs
    * pkg:github/dosfstools/dosfstools
    * pkg:github/google/brotli
    * pkg:github/hewlettpackard/wireless-tools
    * pkg:github/inotify-tools/inotify-tools
    * pkg:github/libbpf/bpftool
    * pkg:github/llvm/llvm-project
    * pkg:github/nixos/nix
    * pkg:github/plougher/squashfs-tools
    * pkg:github/pupnp/pupnp
    * pkg:github/python/cpython
    * pkg:github/rpm-software-management/rpm
    * pkg:github/shadow-maint/shadow
    * pkg:github/sqlite/sqlite
    * pkg:github/u-boot/u-boot


v0.4.0
-------
- FetchCode now supports retrieving package info for following generic packages:
    ``busybox``, ``bzip2``, ``dnsmasq``, ``dropbear``, ``ebtables``, ``hostapd``, ``ipkg``,
    ``iproute2``, ``iptables``, ``libnl``, ``lighttpd``, ``nftables``, ``openssh``, ``samba``,
    ``syslinux``, ``toybox``, ``uclibc``, ``uclibc-ng``, ``util-linux`` and ``wpa_supplicant``.
- FetchCode also supports retrieving package info for GNU packages.


v0.3.0
-------
- Add `package_versions` for retrieving all released versions of a given package.


v0.2.0
-------

- Don't delete temp directory in fetch_via_vcs

v0.1.0
---------

First, initial release.
