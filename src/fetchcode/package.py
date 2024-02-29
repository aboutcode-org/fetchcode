# fetchcode is a free software tool from nexB Inc. and others.
# Visit https://github.com/nexB/fetchcode for support and download.
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and http://aboutcode.org
#
# This software is licensed under the Apache License version 2.0.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at:
# http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import dataclasses
import re
import time
from datetime import datetime
from typing import List
from urllib.parse import urljoin

import htmllistparse
import requests
from commoncode.version import hint
from packageurl import PackageURL
from packageurl.contrib.route import NoRouteAvailable
from packageurl.contrib.route import Router

from fetchcode.packagedcode_models import Package

router = Router()


def info(url):
    """
    Return data according to the `url` string
    `url` string can be purl too
    """
    if url:
        try:
            return router.process(url)
        except NoRouteAvailable:
            return


def get_response(url):
    """
    Generate `Package` object for a `url` string
    """
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()

    raise Exception(f"Failed to fetch: {url}")


def get_pypi_bugtracker_url(project_urls):
    bug_tracking_url = project_urls.get("Tracker")
    if not (bug_tracking_url):
        bug_tracking_url = project_urls.get("Issue Tracker")
    if not (bug_tracking_url):
        bug_tracking_url = project_urls.get("Bug Tracker")
    return bug_tracking_url


def get_pypi_codeview_url(project_urls):
    code_view_url = project_urls.get("Source")
    if not (code_view_url):
        code_view_url = project_urls.get("Code")
    if not (code_view_url):
        code_view_url = project_urls.get("Source Code")
    return code_view_url


@router.route("pkg:cargo/.*")
def get_cargo_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of cargo type
    """
    purl = PackageURL.from_string(purl)
    base_url = "https://crates.io"
    name = purl.name
    version = purl.version
    api_url = f"{base_url}/api/v1/crates/{name}"
    download_url = f"{api_url}/{version}/download" if version else None
    response = get_response(api_url)
    crate = response.get("crate") or {}
    homepage_url = crate.get("homepage")
    code_view_url = crate.get("repository")
    yield Package(
        homepage_url=homepage_url,
        api_url=api_url,
        code_view_url=code_view_url,
        download_url=download_url,
        **purl.to_dict(),
    )
    versions = response.get("versions", [])
    for version in versions:
        version_purl = PackageURL(type=purl.type, name=name, version=version.get("num"))
        dl_path = version.get("dl_path")
        if dl_path:
            download_url = f"{base_url}/{dl_path}"
        else:
            download_url = None
        declared_license = version.get("license")

        yield Package(
            homepage_url=homepage_url,
            api_url=api_url,
            code_view_url=code_view_url,
            download_url=download_url,
            declared_license=declared_license,
            **version_purl.to_dict(),
        )


@router.route("pkg:npm/.*")
def get_npm_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of npm type
    """
    purl = PackageURL.from_string(purl)
    base_path = "http://registry.npmjs.org"
    name = purl.name
    version = purl.version
    api_url = f"{base_path}/{name}"
    response = get_response(api_url)
    vcs_data = response.get("repository") or {}
    bugs = response.get("bugs") or {}

    download_url = f"{base_path}/{name}/-/{name}-{version}.tgz" if version else None
    vcs_url = vcs_data.get("url")
    bug_tracking_url = bugs.get("url")
    license = response.get("license")
    homepage_url = response.get("homepage")

    yield Package(
        homepage_url=homepage_url,
        api_url=api_url,
        vcs_url=vcs_url,
        bug_tracking_url=bug_tracking_url,
        download_url=download_url,
        declared_license=license,
        **purl.to_dict(),
    )

    versions = response.get("versions", [])
    tags = []
    for num in versions:
        version = versions[num]
        version_purl = PackageURL(
            type=purl.type, name=name, version=version.get("version")
        )
        repository = version.get("repository") or {}
        bugs = response.get("bugs") or {}
        dist = version.get("dist") or {}
        licenses = version.get("licenses") or [{}]
        vcs_url = repository.get("url")
        download_url = dist.get("tarball")
        bug_tracking_url = bugs.get("url")
        declared_license = licenses[0].get("type")

        yield Package(
            homepage_url=homepage_url,
            api_url=api_url,
            vcs_url=vcs_url,
            bug_tracking_url=bug_tracking_url,
            download_url=download_url,
            declared_license=declared_license,
            **version_purl.to_dict(),
        )


@router.route("pkg:pypi/.*")
def get_pypi_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of npm type
    """
    purl = PackageURL.from_string(purl)
    name = purl.name
    base_path = "https://pypi.org/pypi"
    api_url = f"{base_path}/{name}/json"
    response = get_response(api_url)
    releases = response.get("releases") or {}
    info = response.get("info") or {}
    homepage_url = info.get("home_page")
    license = info.get("license")
    project_urls = info.get("project_urls") or {}
    code_view_url = get_pypi_codeview_url(project_urls)
    bug_tracking_url = get_pypi_bugtracker_url(project_urls)
    yield Package(
        homepage_url=homepage_url,
        api_url=api_url,
        bug_tracking_url=bug_tracking_url,
        code_view_url=code_view_url,
        declared_license=license,
        **purl.to_dict(),
    )
    for num in releases:
        version_purl = PackageURL(type=purl.type, name=name, version=num)
        release = releases.get(num) or [{}]
        release = release[0]
        download_url = release.get("url")
        yield Package(
            homepage_url=homepage_url,
            api_url=api_url,
            bug_tracking_url=bug_tracking_url,
            code_view_url=code_view_url,
            download_url=download_url,
            declared_license=license,
            **version_purl.to_dict(),
        )


@router.route("pkg:github/.*")
def get_github_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of github type
    """
    purl = PackageURL.from_string(purl)
    name = purl.name
    namespace = purl.namespace
    base_path = "https://api.github.com/repos"
    api_url = f"{base_path}/{namespace}/{name}"
    response = get_response(api_url)
    homepage_url = response.get("homepage")
    vcs_url = response.get("git_url")
    github_url = "https://github.com"
    bug_tracking_url = f"{github_url}/{namespace}/{name}/issues"
    code_view_url = f"{github_url}/{namespace}/{name}"
    license_data = response.get("license") or {}
    declared_license = license_data.get("spdx_id")
    primary_language = response.get("language")
    yield Package(
        homepage_url=homepage_url,
        vcs_url=vcs_url,
        api_url=api_url,
        bug_tracking_url=bug_tracking_url,
        code_view_url=code_view_url,
        declared_license=declared_license,
        primary_language=primary_language,
        **purl.to_dict(),
    )
    release_url = f"{api_url}/releases"
    releases = get_response(release_url)
    for release in releases:
        version = release.get("name")
        version_purl = PackageURL(
            type=purl.type, namespace=namespace, name=name, version=version
        )
        download_url = release.get("tarball_url")
        code_view_url = f"{github_url}/{namespace}/{name}/tree/{version}"
        version_vcs_url = f"{vcs_url}@{version}"
        yield Package(
            homepage_url=homepage_url,
            vcs_url=version_vcs_url,
            api_url=api_url,
            bug_tracking_url=bug_tracking_url,
            code_view_url=code_view_url,
            declared_license=declared_license,
            primary_language=primary_language,
            download_url=download_url,
            **version_purl.to_dict(),
        )


@router.route("pkg:bitbucket/.*")
def get_bitbucket_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of bitbucket type
    """
    purl = PackageURL.from_string(purl)
    name = purl.name
    namespace = purl.namespace
    base_path = "https://api.bitbucket.org/2.0/repositories"
    api_url = f"{base_path}/{namespace}/{name}"
    response = get_response(api_url)
    bitbucket_url = "https://bitbucket.org"
    bug_tracking_url = f"{bitbucket_url}/{namespace}/{name}/issues"
    code_view_url = f"{bitbucket_url}/{namespace}/{name}"
    yield Package(
        api_url=api_url,
        bug_tracking_url=bug_tracking_url,
        code_view_url=code_view_url,
        **purl.to_dict(),
    )
    links = response.get("links") or {}
    tags_url = links.get("tags") or {}
    tags_url = tags_url.get("href")
    if not tags_url:
        return []
    tags_data = get_response(tags_url)
    tags = tags_data.get("values") or {}
    for tag in tags:
        version = tag.get("name") or ""
        version_purl = PackageURL(
            type=purl.type, namespace=namespace, name=name, version=version
        )
        download_url = (
            f"{base_path}/{namespace}/{name}/downloads/{name}-{version}.tar.gz"
        )
        code_view_url = f"{bitbucket_url}/{namespace}/{name}/src/{version}"
        yield Package(
            api_url=api_url,
            bug_tracking_url=bug_tracking_url,
            code_view_url=code_view_url,
            download_url=download_url,
            **version_purl.to_dict(),
        )


@router.route("pkg:rubygems/.*")
def get_rubygems_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of rubygems type
    """
    purl = PackageURL.from_string(purl)
    name = purl.name
    api_url = f"https://rubygems.org/api/v1/gems/{name}.json"
    response = get_response(api_url)
    declared_license = response.get("licenses") or None
    homepage_url = response.get("homepage_uri")
    code_view_url = response.get("source_code_uri")
    bug_tracking_url = response.get("bug_tracker_uri")
    download_url = response.get("gem_uri")
    yield Package(
        homepage_url=homepage_url,
        api_url=api_url,
        bug_tracking_url=bug_tracking_url,
        code_view_url=code_view_url,
        declared_license=declared_license,
        download_url=download_url,
        **purl.to_dict(),
    )


@router.route("pkg:gnu/.*")
def get_gnu_data_from_purl(purl):
    """Generate `Package` object from the `purl` string of gnu type"""
    purl = PackageURL.from_string(purl)
    source_archive_url = f"https://ftp.gnu.org/pub/gnu/{purl.name}/"
    regex = r"^({}-)[\w.]*(.tar.gz)$".format(purl.name)

    yield from extract_packages_from_listing(purl, source_archive_url, regex)


@dataclasses.dataclass
class DirectoryListedSource:
    source_url: str = dataclasses.field(
        default="", metadata={"description": "URL of the directory listing source"}
    )
    is_nested: bool = dataclasses.field(
        default=False,
        metadata={
            "description": "Flag indicating whether the archives are nested within another directory"
        },
    )
    source_archive_regex: str = dataclasses.field(
        default="",
        metadata={
            "description": "Regular expression pattern to match files in the directory listing."
        },
    )
    ignored_files_and_dir: List[str] = dataclasses.field(
        default_factory=list,
        metadata={
            "description": "List of files and directories to ignore in the directory listing."
        },
    )

    # TODO: use ignored_files_and_dir to ignore non interesting archives.
    @classmethod
    def get_package_info(cls, purl):
        package_url = PackageURL.from_string(purl)
        if cls.is_nested:
            _, listing = htmllistparse.fetch_listing(cls.source_url)
            for dir in listing:
                if not dir.name.endswith("/"):
                    continue
                url = urljoin(cls.source_url, dir.name)
                yield from extract_packages_from_listing(
                    package_url, url, cls.source_archive_regex
                )
        else:
            yield from extract_packages_from_listing(
                package_url, cls.source_url, cls.source_archive_regex
            )


class IpkgDirectoryListedSource(DirectoryListedSource):
    source_url = "https://web.archive.org/web/20090326020239/http://handhelds.org/download/packages/ipkg/"
    is_nested = False
    source_archive_regex = r"^(ipkg[-_])[\w.]*(_arm.ipk|.tar.gz)$"
    ignored_files_and_dir = []


class UtilLinuxDirectoryListedSource(DirectoryListedSource):
    source_url = "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/"
    is_nested = True
    source_archive_regex = r"^(util-linux-)[\w.]*(.tar.gz)$"
    ignored_files_and_dir = []


class BusyBoxDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.busybox.net/downloads/"
    source_archive_regex = r"^(busybox-)[\w.]*(.tar.bz2)$"
    is_nested = False
    ignored_files_and_dir = []


class UclibcDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.uclibc.org/downloads/"
    source_archive_regex = r"^(uClibc-)[\w.]*(.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class UclibcNGDirectoryListedSource(DirectoryListedSource):
    source_url = "https://downloads.uclibc-ng.org/releases/"
    source_archive_regex = r"^(uClibc-ng-)[\w.]*(.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class Bzip2DirectoryListedSource(DirectoryListedSource):
    source_url = "https://sourceware.org/pub/bzip2/"
    source_archive_regex = r"^(bzip2-)[\w.]*(.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class OpenSSHDirectoryListedSource(DirectoryListedSource):
    source_url = "https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/"
    source_archive_regex = r"^(openssh-)[\w.]*(.tgz|.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class DnsmasqDirectoryListedSource(DirectoryListedSource):
    source_url = "https://thekelleys.org.uk/dnsmasq/"
    source_archive_regex = r"^(dnsmasq-)[\w.]*(.tar.xz|.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class EbtablesDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.netfilter.org/pub/ebtables/"
    source_archive_regex = r"^(ebtables-)[\w.]*(.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class HostapdDirectoryListedSource(DirectoryListedSource):
    source_url = "https://w1.fi/releases/"
    source_archive_regex = r"^(hostapd-)[\w.]*(.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class Iproute2DirectoryListedSource(DirectoryListedSource):
    source_url = "https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/"
    source_archive_regex = r"^(iproute2-)[\w.]*(.tar.xz|.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class IptablesDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.netfilter.org/pub/iptables/"
    source_archive_regex = r"^(iptables-)[\w.]*(.tar.bz2)$"
    is_nested = False
    ignored_files_and_dir = []


class LibnlDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.infradead.org/~tgr/libnl/files/"
    source_archive_regex = r"^(libnl-)[\w.]*(.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class LighttpdDirectoryListedSource(DirectoryListedSource):
    source_url = "https://download.lighttpd.net/lighttpd/releases-1.4.x/"
    source_archive_regex = r"^(lighttpd-)[\w.]*(.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class NftablesDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.netfilter.org/pub/nftables/"
    source_archive_regex = r"^(nftables-)[\w.]*(.tar.xz|.tar.bz2)$"
    is_nested = False
    ignored_files_and_dir = []


class WpaSupplicantDirectoryListedSource(DirectoryListedSource):
    source_url = "https://w1.fi/releases/"
    source_archive_regex = r"^(wpa_supplicant-)[\w.]*(.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class SyslinuxDirectoryListedSource(DirectoryListedSource):
    source_url = "https://mirrors.edge.kernel.org/pub/linux/utils/boot/syslinux/"
    source_archive_regex = r"^(syslinux-)[\w.]*(.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class SyslinuxDirectoryListedSource(DirectoryListedSource):
    source_url = "https://mirrors.edge.kernel.org/pub/linux/utils/boot/syslinux/"
    source_archive_regex = r"^(syslinux-)[\w.]*(.tar.gz)$"
    is_nested = False
    ignored_files_and_dir = []


class ToyboxDirectoryListedSource(DirectoryListedSource):
    source_url = "http://www.landley.net/toybox/downloads/"
    source_archive_regex = r"^(toybox-)[\w.]*(.tar.gz|.tar.bz2)$"
    is_nested = False
    ignored_files_and_dir = []


class DropbearDirectoryListedSource(DirectoryListedSource):
    source_url = "https://matt.ucc.asn.au/dropbear/releases/"
    source_archive_regex = r"^(dropbear-)[\w.]*(.tar.bz2|_i386.deb)$"
    is_nested = False
    ignored_files_and_dir = []


HTML_DIR_LIST = {
    "pkg:generic/ipkg": IpkgDirectoryListedSource,
    "pkg:generic/util-linux": UtilLinuxDirectoryListedSource,
    "pkg:generic/busybox": BusyBoxDirectoryListedSource,
    "pkg:generic/uclibc": UclibcDirectoryListedSource,
    "pkg:generic/uclibc-ng": UclibcNGDirectoryListedSource,
    "pkg:generic/bzip2": Bzip2DirectoryListedSource,
    "pkg:generic/openssh": OpenSSHDirectoryListedSource,
    "pkg:generic/dnsmasq": DnsmasqDirectoryListedSource,
    "pkg:generic/ebtables": EbtablesDirectoryListedSource,
    "pkg:generic/hostapd": HostapdDirectoryListedSource,
    "pkg:generic/iproute2": Iproute2DirectoryListedSource,
    "pkg:generic/iptables": IptablesDirectoryListedSource,
    "pkg:generic/libnl": LibnlDirectoryListedSource,
    "pkg:generic/lighttpd": LighttpdDirectoryListedSource,
    "pkg:generic/nftables": NftablesDirectoryListedSource,
    "pkg:generic/wpa_supplicant": WpaSupplicantDirectoryListedSource,
    "pkg:generic/syslinux": SyslinuxDirectoryListedSource,
    # TODO: Need to implement extraction from deep nested directory.
    #    "pkg:generic/rpm":
    #    source_url ="https://ftp.osuosl.org/pub/rpm/releases/"
    #    source_archive_regex = r"^(rpm-)[\w.]*(.tar.bz2)$"
    #    is_nested = False
    "pkg:generic/toybox": ToyboxDirectoryListedSource,
    # TODO: Ignore test archives like dropbear-0.44test4.tar.gz
    "pkg:generic/dropbear": DropbearDirectoryListedSource,
}


@router.route(*HTML_DIR_LIST.keys())
def get_htmllisting_data_from_purl(purl):
    """Generate `Package` object from the `purl` having directory listed source"""
    return HTML_DIR_LIST[purl].get_package_info(purl)


def extract_packages_from_listing(purl, source_archive_url, regex):
    """
    Yield package data from a directory listing for given source_archive_url.
    """
    pattern = re.compile(regex)
    _, listing = htmllistparse.fetch_listing(source_archive_url)
    for file in listing:
        if not pattern.match(file.name):
            continue

        version = hint(file.name)
        if not version:
            continue

        version = version.strip("v").strip()
        modified_time = file.modified
        date = datetime.utcfromtimestamp(time.mktime(modified_time))

        download_url = urljoin(source_archive_url, file.name)
        package_url = PackageURL(
            type=purl.type, namespace=purl.namespace, name=purl.name, version=version
        )
        yield Package(
            homepage_url=source_archive_url,
            download_url=download_url,
            release_date=date.isoformat(),
            **package_url.to_dict(),
        )
