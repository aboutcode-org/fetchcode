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
import logging
import os
import re

import attr
from bs4 import BeautifulSoup
from univers import versions

from fetchcode import utils
from fetchcode.packagedcode_models import Package

LOG_FILE_LOCATION = os.path.join(os.path.expanduser("~"), "purlcli.log")
logger = logging.getLogger(__name__)


def package_from_dict(package_data):
    """
    Return a Package built from a `package_data` mapping.
    Ignore unknown and unsupported fields.
    """
    supported = {attr.name for attr in attr.fields(Package)}
    cleaned_package_data = {
        key: value for key, value in package_data.items() if key in supported
    }
    return Package(**cleaned_package_data)


@dataclasses.dataclass
class GitHubSource:
    version_regex: re.Pattern = dataclasses.field(
        default=None,
        metadata={
            "help_text": "Regular expression pattern to match and extract version from tag."
        },
    )
    ignored_tag_regex: re.Pattern = dataclasses.field(
        default=None,
        metadata={"help_text": "Regex to ignore tag."},
    )

    @classmethod
    def get_default_package(cls, purl):
        """Return a Package object populated with default for this data source."""
        name = purl.name
        namespace = purl.namespace
        base_path = "https://api.github.com/repos"
        api_url = f"{base_path}/{namespace}/{name}"
        response = utils.get_github_rest(api_url)
        homepage_url = response.get("homepage")
        vcs_url = response.get("git_url")
        github_url = "https://github.com"
        bug_tracking_url = f"{github_url}/{namespace}/{name}/issues"
        code_view_url = f"{github_url}/{namespace}/{name}"
        license_data = response.get("license") or {}
        declared_license = license_data.get("spdx_id")
        primary_language = response.get("language")
        return Package(
            homepage_url=homepage_url,
            vcs_url=vcs_url,
            api_url=api_url,
            bug_tracking_url=bug_tracking_url,
            code_view_url=code_view_url,
            declared_license=declared_license,
            primary_language=primary_language,
            **purl.to_dict(),
        )

    @classmethod
    def get_package_info(cls, package_url):
        yield from get_github_packages(
            package_url,
            cls.version_regex,
            cls.ignored_tag_regex,
            cls.get_default_package(package_url),
        )


def get_github_packages(purl, version_regex, ignored_tag_regex, default_package):
    """
    Yield package data from a directory listing for the given source_archive_url.
    """
    for package in _get_github_packages(
        purl, version_regex, ignored_tag_regex, default_package
    ):
        # Don't yield all packages when a specific version is requested.
        if purl.version and package.version != purl.version:
            continue

        yield package

        # If a version is specified in purl and we have found a matching package,
        # we don't need to continue searching.
        if purl.version:
            break


def _get_github_packages(purl, version_regex, ignored_tag_regex, default_package):
    "Yield package for GitHub purl"
    archive_download_url = (
        "https://github.com/{org}/{name}/archive/refs/tags/{tag_name}.tar.gz"
    )

    package_dict = default_package.to_dict()
    for tag, date in utils.fetch_github_tags_gql(purl):
        if ignored_tag_regex and ignored_tag_regex.match(tag):
            continue

        if version_regex:
            match = version_regex.match(tag)
            if not match:
                continue
            version = match.group("version")
        else:
            version = tag

        version = version.strip("Vv").strip()
        if "+" in version:
            first, last = version.split("+")
            first.replace("_", ".")
            version = f"{first}+{last}"
        else:
            version = version.replace("_", ".")
        if not version or not version[0].isdigit():
            continue

        download_url = archive_download_url.format(
            org=purl.namespace, name=purl.name, tag_name=tag
        )

        date = date.strftime("%Y-%m-%dT%H:%M:%S")
        package_dict.update(
            {
                "download_url": download_url,
                "release_date": date,
                "version": version,
            }
        )

        yield package_from_dict(package_dict)


class UBootGitHubSource(GitHubSource):
    version_regex = re.compile(r"(?P<version>v\d{4}\.\d{2})(?![\w.-])")
    ignored_tag_regex = None


class Genext2fsGitHubSource(GitHubSource):
    version_regex = None
    ignored_tag_regex = re.compile(r"debian_version\S+upstream_version\S+")


class SquashfsToolsGitHubSource(GitHubSource):
    version_regex = re.compile(r"\b[vV]?(?P<version>(?:\d+(\.\d+){1,2}))\b")
    ignored_tag_regex = None


class PupnpGitHubSource(GitHubSource):
    version_regex = re.compile(r"\brelease-?(?P<version>(?:\d+(\.\d+){1,2}))\b")
    ignored_tag_regex = None


class BrotliGitHubSource(GitHubSource):
    version_regex = re.compile(r"\b[vV]?(?P<version>(?:\d+(\.\d+){1,2}))\b")
    ignored_tag_regex = None


class BpftoolGitHubSource(GitHubSource):
    version_regex = re.compile(r"\b[vV]?(?P<version>(?:\d+(\.\d+){1,2}))\b")
    ignored_tag_regex = None


class SqliteGitHubSource(GitHubSource):
    version_regex = re.compile(r"\bversion-?(?P<version>(?:\d+(\.\d+){1,2}))\b")
    ignored_tag_regex = None


class LlvmGitHubSource(GitHubSource):
    version_regex = re.compile(r"llvmorg-(?P<version>.+)")
    ignored_tag_regex = None


class RpmGitHubSource(GitHubSource):
    version_regex = re.compile(r"rpm-(?P<version>[^-]+(?:-(?!release).*)?|-release)")
    ignored_tag_regex = None


GITHUB_SOURCE_BY_PACKAGE = {
    "avahi/avahi": GitHubSource,
    "bestouff/genext2fs": Genext2fsGitHubSource,
    "dosfstools/dosfstools": GitHubSource,
    "google/brotli": BrotliGitHubSource,
    "hewlettpackard/wireless-tools": GitHubSource,
    "inotify-tools/inotify-tools": GitHubSource,
    "libbpf/bpftool": BpftoolGitHubSource,
    "llvm/llvm-project": LlvmGitHubSource,
    "nixos/nix": GitHubSource,
    "plougher/squashfs-tools": SquashfsToolsGitHubSource,
    "pupnp/pupnp": PupnpGitHubSource,
    "python/cpython": GitHubSource,
    "rpm-software-management/rpm": RpmGitHubSource,
    "shadow-maint/shadow": GitHubSource,
    "sqlite/sqlite": SqliteGitHubSource,
    "u-boot/u-boot": UBootGitHubSource,
}


class OpenSSLGitHubSource(GitHubSource):
    version_regex = re.compile(r"(OpenSSL_|openssl-)(?P<version>.+)")
    ignored_tag_regex = None

    @classmethod
    def get_package_info(cls, gh_purl):

        packages = get_github_packages(
            gh_purl,
            cls.version_regex,
            cls.ignored_tag_regex,
            cls.get_default_package(gh_purl),
        )

        for package in packages:
            package_dict = package.to_dict()
            package_dict["type"] = "openssl"
            package_dict["namespace"] = None
            package_dict["name"] = "openssl"
            package_dict["version"] = package_dict["version"]

            yield package_from_dict(package_dict)


class ErofsUtilsGitHubSource(GitHubSource):
    version_regex = None
    ignored_tag_regex = None

    @classmethod
    def get_package_info(cls, gh_purl):

        packages = get_github_packages(
            gh_purl,
            cls.version_regex,
            cls.ignored_tag_regex,
            cls.get_default_package(gh_purl),
        )

        for package in packages:
            package_dict = package.to_dict()
            package_dict["type"] = "generic"
            package_dict["namespace"] = None
            package_dict["name"] = "erofs-utils"
            package_dict["version"] = package_dict["version"]

            yield package_from_dict(package_dict)


class MiniupnpPackagesGitHubSource(GitHubSource):
    version_regex = None
    ignored_tag_regex = None
    version_regex_template = r"{}_(?P<version>.+)"

    @classmethod
    def get_package_info(cls, gh_purl, package_name):
        cls.version_regex = re.compile(
            cls.version_regex_template.format(re.escape(package_name))
        )

        packages = get_github_packages(
            gh_purl,
            cls.version_regex,
            cls.ignored_tag_regex,
            cls.get_default_package(gh_purl),
        )

        for package in packages:
            package_dict = package.to_dict()
            package_dict["type"] = "generic"
            package_dict["namespace"] = None
            package_dict["name"] = package_name
            package_dict["version"] = package_dict["version"]

            yield package_from_dict(package_dict)


# Archive source https://web.archive.org/web/20021209021312/http://udhcp.busybox.net/source/
UDHCP_RELEASES = {
    "0.9.1": {
        "url": "https://web.archive.org/web/20021209021312/http://udhcp.busybox.net/source//udhcp-0.9.1.tar.gz",
        "date": "2001-08-10T20:17:00",
    },
    "0.9.2": {
        "url": "https://web.archive.org/web/20021209021312/http://udhcp.busybox.net/source//udhcp-0.9.2.tar.gz",
        "date": "2001-08-10T20:17:00",
    },
    "0.9.3": {
        "url": "https://web.archive.org/web/20021209021312/http://udhcp.busybox.net/source//udhcp-0.9.3.tar.gz",
        "date": "2001-08-20T18:23:00",
    },
    "0.9.4": {
        "url": "https://web.archive.org/web/20021209021312/http://udhcp.busybox.net/source//udhcp-0.9.4.tar.gz",
        "date": "2001-08-27T15:41:00",
    },
    "0.9.5": {
        "url": "https://web.archive.org/web/20021209021312/http://udhcp.busybox.net/source//udhcp-0.9.5.tar.gz",
        "date": "2001-09-14T18:19:00",
    },
    "0.9.6": {
        "url": "https://web.archive.org/web/20021209021312/http://udhcp.busybox.net/source//udhcp-0.9.6.tar.gz",
        "date": "2001-10-01T13:38:00",
    },
    "0.9.7": {
        "url": "https://web.archive.org/web/20021209021312/http://udhcp.busybox.net/source//udhcp-0.9.7.tar.gz",
        "date": "2002-05-27T00:48:00",
    },
    "0.9.8": {
        "url": "https://web.archive.org/web/20021209021312/http://udhcp.busybox.net/source//udhcp-0.9.8.tar.gz",
        "date": "2002-10-31T12:10:00",
    },
}


# Since there will be no new releases of ipkg, it's better to
# store them in a dictionary rather than fetching them every time.
IPKG_RELEASES = {
    "0.99.88": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.88.tar.gz",
        "date": "2003-08-08T03:03:00",
    },
    "0.99.89": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.89.tar.gz",
        "date": "2003-08-21T10:02:00",
    },
    "0.99.102": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.102.tar.gz",
        "date": "2003-11-10T09:58:00",
    },
    "0.99.107": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.107.tar.gz",
        "date": "2004-01-12T06:08:00",
    },
    "0.99.110": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.110.tar.gz",
        "date": "2004-01-18T15:52:00",
    },
    "0.99.118": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.118.tar.gz",
        "date": "2004-03-29T11:25:00",
    },
    "0.99.119": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.119.tar.gz",
        "date": "2004-04-06T12:14:00",
    },
    "0.99.120": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.120.tar.gz",
        "date": "2004-04-07T12:50:00",
    },
    "0.99.121": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.121.tar.gz",
        "date": "2004-05-03T09:58:00",
    },
    "0.99.122-1": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.122-1.tar.gz",
        "date": "2004-05-14T12:51:00",
    },
    "0.99.122-2": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.122-2.tar.gz",
        "date": "2004-05-16T05:02:00",
    },
    "0.99.122-3": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.122-3.tar.gz",
        "date": "2004-05-16T05:49:00",
    },
    "0.99.122": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.122.tar.gz",
        "date": "2004-05-10T12:13:00",
    },
    "0.99.124": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.124.tar.gz",
        "date": "2004-05-21T11:29:00",
    },
    "0.99.125": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.125.tar.gz",
        "date": "2004-06-05T09:58:00",
    },
    "0.99.126": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.126.tar.gz",
        "date": "2004-06-15T11:51:00",
    },
    "0.99.127": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.127.tar.gz",
        "date": "2004-07-20T11:50:00",
    },
    "0.99.129": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.129.tar.gz",
        "date": "2004-09-01T12:15:00",
    },
    "0.99.130": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.130.tar.gz",
        "date": "2004-09-11T11:27:00",
    },
    "0.99.131": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.131.tar.gz",
        "date": "2004-09-30T10:05:00",
    },
    "0.99.132": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.132.tar.gz",
        "date": "2004-10-17T10:26:00",
    },
    "0.99.133": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.133.tar.gz",
        "date": "2004-11-18T09:49:00",
    },
    "0.99.134": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.134.tar.gz",
        "date": "2005-01-05T14:42:00",
    },
    "0.99.135": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.135.tar.gz",
        "date": "2005-01-06T02:59:00",
    },
    "0.99.136": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.136.tar.gz",
        "date": "2005-01-10T11:00:00",
    },
    "0.99.137": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.137.tar.gz",
        "date": "2005-01-10T12:11:00",
    },
    "0.99.138": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.138.tar.gz",
        "date": "2005-01-18T12:19:00",
    },
    "0.99.139": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.139.tar.gz",
        "date": "2005-02-05T11:40:00",
    },
    "0.99.140": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.140.tar.gz",
        "date": "2005-02-05T13:16:00",
    },
    "0.99.141": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.141.tar.gz",
        "date": "2005-02-06T12:16:00",
    },
    "0.99.142": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.142.tar.gz",
        "date": "2005-02-07T12:51:00",
    },
    "0.99.143": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.143.tar.gz",
        "date": "2005-02-20T09:26:00",
    },
    "0.99.144": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.144.tar.gz",
        "date": "2005-02-22T12:52:00",
    },
    "0.99.145": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.145.tar.gz",
        "date": "2005-03-14T11:59:00",
    },
    "0.99.146": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.146.tar.gz",
        "date": "2005-03-28T10:02:00",
    },
    "0.99.148": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.148.tar.gz",
        "date": "2005-04-10T11:26:00",
    },
    "0.99.149": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.149.tar.gz",
        "date": "2005-05-13T10:41:00",
    },
    "0.99.151": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.151.tar.gz",
        "date": "2005-06-16T09:39:00",
    },
    "0.99.152": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.152.tar.gz",
        "date": "2005-07-06T03:38:00",
    },
    "0.99.153": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.153.tar.gz",
        "date": "2005-07-29T11:02:00",
    },
    "0.99.154": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.154.tar.gz",
        "date": "2005-09-16T10:41:00",
    },
    "0.99.155": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.155.tar.gz",
        "date": "2006-01-04T11:55:00",
    },
    "0.99.156": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.156.tar.gz",
        "date": "2006-01-14T09:56:00",
    },
    "0.99.157": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.157.tar.gz",
        "date": "2006-01-22T10:30:00",
    },
    "0.99.158": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.158.tar.gz",
        "date": "2006-02-02T11:47:00",
    },
    "0.99.161": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.161.tar.gz",
        "date": "2006-04-19T10:15:00",
    },
    "0.99.162": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.162.tar.gz",
        "date": "2006-05-29T23:02:00",
    },
    "0.99.163": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg-0.99.163.tar.gz",
        "date": "2006-05-29T23:40:00",
    },
    "0.9-1": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-1_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-2": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-2_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-3": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-3_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-4": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-4_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-5": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-5_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-6": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-6_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-6a": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-6a_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-6b": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-6b_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-6c": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-6c_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-demo3": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-demo3_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-demo4": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-demo4_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-demo5": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-demo5_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-demo6": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-demo6_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-jeh1": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-jeh1_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-jeh3": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-jeh3_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-jeh4": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-jeh4_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-jeh5": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-jeh5_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-jeh6": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-jeh6_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.9-jeh7": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-jeh7_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.9-jeh8": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-jeh8_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.9-jehb": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-jehb_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.9-jehc": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9-jehc_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.9": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.9_arm.ipk",
        "date": "2001-12-07T03:11:00",
    },
    "0.99.8": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.8_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.9-1": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.9-1_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.9-2": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.9-2_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.9-3": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.9-3_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.9": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.9_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.10-2": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.10-2_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.10": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.10_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.11": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.11_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.13": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.13_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.14": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.14_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.15": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.15_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.16": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.16_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.18": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.18_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.19": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.19_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.20": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.20_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.21": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.21_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.22": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.22_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.23": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.23_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.24": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.24_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.27": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.27_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.28-1": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.28-1_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.28": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.28_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.29": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.29_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.31": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.31_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.32": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.32_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.33": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.33_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
    "0.99.34": {
        "url": "https://web.archive.org/web/20090326020239/http:/handhelds.org/download/packages/ipkg/ipkg_0.99.34_arm.ipk",
        "date": "2002-08-19T04:23:00",
    },
}


def get_cocoapods_org_url_status(purl, name, cocoapods_org_url):
    purl_to_cocoapods_org_url_status = {}
    cocoapods_org_url_head_request = utils.make_head_request(cocoapods_org_url)
    cocoapods_org_url_status_code = cocoapods_org_url_head_request.status_code

    if cocoapods_org_url_status_code == 404:
        logger.error(f"cocoapods_org_url not found for {name}")
        purl_to_cocoapods_org_url_status["return_message"] = "cocoapods_org_url_not_found"
        return purl_to_cocoapods_org_url_status
    elif cocoapods_org_url_status_code == 503:
        logger.error(f"cocoapods_org_url temporarily unavailable for {name}")
        purl_to_cocoapods_org_url_status["return_message"] = "cocoapods_org_url_temporarily_unavailable"
        return purl_to_cocoapods_org_url_status
    elif cocoapods_org_url_status_code == 302:
        redirect_url = cocoapods_org_url_head_request.headers['Location']
        redirect_message = f"The cocoapods.org URL {cocoapods_org_url} redirects to {redirect_url}"
        logger.warning(redirect_message)
        print(redirect_message)

        gh_repo_namespace = None
        gh_repo_name = None
        if redirect_url.startswith("https://github.com/"):
            redirect_url_split = redirect_url.split("/")
            if len(redirect_url_split) < 3:
                return purl_to_cocoapods_org_url_status
            gh_repo_namespace = redirect_url_split[-2]
            gh_repo_name = redirect_url_split[-1]

            redirect_to_gh_response = utils.get_complete_response(redirect_url)
            if "Failed to fetch" in redirect_to_gh_response:
                logger.error(redirect_to_gh_response)
                print(redirect_to_gh_response)
                purl_to_cocoapods_org_url_status["return_message"] = "failed_to_fetch_github_redirect"
                return purl_to_cocoapods_org_url_status
            elif "not_found" in redirect_to_gh_response:
                redirect_to_gh_not_found = f"Redirect to GitHub not found: {redirect_url}"
                logger.error(redirect_to_gh_not_found)
                print(redirect_to_gh_not_found)
                purl_to_cocoapods_org_url_status["return_message"] = "github_redirect_not_found"
                return purl_to_cocoapods_org_url_status

            soup = BeautifulSoup(redirect_to_gh_response.text, "html.parser")
            head = soup.find("head")
            og_url_tag_get_content = None
            corrected_name = None
            if head:
                og_url_tag = head.find("meta", property="og:url")
                if og_url_tag:
                    og_url = og_url_tag.get("content")
                    og_url_tag_get_content = og_url
                    corrected_name = og_url_tag_get_content.split('/')[-1]
                else:
                    no_meta_tag = f"'og:url' meta tag not found in redirect_to_gh_response page for {purl}"
                    print(no_meta_tag)
                    logger.error(no_meta_tag)
                    purl_to_cocoapods_org_url_status["return_message"] = "github_redirect_error"
                    return purl_to_cocoapods_org_url_status
            else:
                no_head_section = f"\n<head> section not found in redirect_to_gh_response page for {purl}"
                print(no_head_section)
                logger.error(no_head_section)
                purl_to_cocoapods_org_url_status["return_message"] = "github_redirect_error"
                return purl_to_cocoapods_org_url_status

            cocoapods_org_version = None

            purl_to_cocoapods_org_url_status["corrected_name"] = corrected_name
            purl_to_cocoapods_org_url_status["cocoapods_org_pod_name"] = corrected_name
            purl_to_cocoapods_org_url_status["cocoapods_org_gh_repo_owner"] = gh_repo_namespace
            purl_to_cocoapods_org_url_status["cocoapods_org_gh_repo_name"] = gh_repo_name
            purl_to_cocoapods_org_url_status["cocoapods_org_version"] = cocoapods_org_version
            purl_to_cocoapods_org_url_status["return_message"] = "cocoapods_org_redirects_to_github"
            return purl_to_cocoapods_org_url_status
        else:
            purl_to_cocoapods_org_url_status["return_message"] = "cocoapods_org_url_redirects"
            return purl_to_cocoapods_org_url_status

    else:
        purl_to_cocoapods_org_url_status["return_message"] = None
        return purl_to_cocoapods_org_url_status


def get_pod_data_with_soup(purl, name, cocoapods_org_url):
    purl_to_pod_data_with_soup = {}
    cocoapods_org_response = utils.get_complete_response(cocoapods_org_url)
    if "Failed to fetch" in cocoapods_org_response:
        logger.error(cocoapods_org_response)
        print(cocoapods_org_response)
        return

    soup = BeautifulSoup(cocoapods_org_response.text, "html.parser")
    cocoapods_org_gh_repo_owner = None
    cocoapods_org_gh_repo_name = None
    cocoapods_org_gh_repo_url = None
    cocoapods_org_podspec_url = None
    cocoapods_org_pkg_home_url = None

    for sidebar_links in (soup.find_all('ul', class_ = "links" )):
        nested_links = sidebar_links.findChildren("a")
        for nested_link in nested_links:
            link_text = nested_link.text
            link_url = nested_link['href']
            if link_text == 'Homepage':
                cocoapods_org_pkg_home_url = link_url
            elif link_text == 'GitHub Repo':
                split_link = link_url.split('/')
                cocoapods_org_gh_repo_owner = split_link[-2]
                cocoapods_org_gh_repo_name = split_link[-1]
            elif link_text == 'See Podspec':
                cocoapods_org_podspec_url = link_url

    if cocoapods_org_gh_repo_owner and cocoapods_org_gh_repo_name:
        cocoapods_org_gh_repo_url = f"https://github.com/{cocoapods_org_gh_repo_owner}/{cocoapods_org_gh_repo_name}"
        cocoapods_org_gh_repo_url_head_request = utils.make_head_request(cocoapods_org_gh_repo_url)
        cocoapods_org_gh_repo_url_status_code = cocoapods_org_gh_repo_url_head_request.status_code
        purl_to_pod_data_with_soup["cocoapods_org_gh_repo_url_status_code"] = cocoapods_org_gh_repo_url_status_code

        base_path = "https://api.github.com/repos"
        api_url = f"{base_path}/{cocoapods_org_gh_repo_owner}/{cocoapods_org_gh_repo_name}"
        github_rest_no_exception_response = utils.get_github_rest_no_exception(api_url)
        if "Failed to fetch" in github_rest_no_exception_response:
            logger.error(f"{github_rest_no_exception_response}")
            print(f"{github_rest_no_exception_response}")

    purl_to_pod_data_with_soup["cocoapods_org_gh_repo_owner"] = cocoapods_org_gh_repo_owner
    purl_to_pod_data_with_soup["cocoapods_org_gh_repo_name"] = cocoapods_org_gh_repo_name
    purl_to_pod_data_with_soup["cocoapods_org_gh_repo_url"] = cocoapods_org_gh_repo_url
    purl_to_pod_data_with_soup["cocoapods_org_podspec_url"] = cocoapods_org_podspec_url
    purl_to_pod_data_with_soup["cocoapods_org_pkg_home_url"] = cocoapods_org_pkg_home_url

    if cocoapods_org_gh_repo_owner is None or cocoapods_org_gh_repo_name is None:
        no_github_repo = f"No GitHub repo found on cocoapods.org for {name}"
        print(f"{no_github_repo}")
        logger.warning(no_github_repo)

    if cocoapods_org_podspec_url is None:
        no_podspec = f"No podspec found on cocoapods.org for {name}"
        print(f"{no_podspec}")
        logger.warning(no_podspec)
        purl_to_pod_data_with_soup["no_podspec"] = no_podspec

    cocoapods_org_version = None
    purl_to_pod_data_with_soup["cocoapods_org_version"] = cocoapods_org_version
    if cocoapods_org_podspec_url:
        cocoapods_org_version = cocoapods_org_podspec_url.split("/")[-2]

    cocoapods_org_pod_name = None
    head = soup.find("head")
    if head:
        og_title_tag = head.find("meta", property="og:title")
        if og_title_tag:
            og_title = og_title_tag.get("content")
            cocoapods_org_pod_name = og_title
        else:
            no_meta_tag = f"'og:title' meta tag not found in cocoapods.org page for {purl}"
            print(no_meta_tag)
            logger.error(no_meta_tag)
    else:
        no_head_section = f"\n<head> section not found in cocoapods.org page for {purl}"
        print(no_head_section)
        logger.error(no_head_section)

    purl_to_pod_data_with_soup["cocoapods_org_pod_name"] = cocoapods_org_pod_name
    input_name = name
    if input_name != cocoapods_org_pod_name:
        name_change = (f"Input PURL name '{input_name}' analyzed as '{cocoapods_org_pod_name}' per {cocoapods_org_url}")
        input_name = cocoapods_org_pod_name
        print(f"{name_change}")
        logger.warning(name_change)

    return purl_to_pod_data_with_soup


def get_cocoapod_tags(spec, cocoapods_org_pod_name):
    try:
        response = utils.get_text_response(spec)
        data = response.strip()
        for line in data.splitlines():
            line = line.strip()
            if line.startswith(cocoapods_org_pod_name):
                data_list = line.split("/")
                if data_list[0] == cocoapods_org_pod_name:
                    data_list.pop(0)
                sorted_data_list = sorted(
                    data_list,
                    key=lambda x: versions.SemverVersion(x),
                    reverse=True,
                )
                return sorted_data_list
        return None
    except:
        print(f"Error retrieving cocoapods tag data from cdn.cocoapods.org")
        return None


def construct_cocoapods_package(
    purl,
    name,
    hashed_path,
    repository_homepage_url,
    cocoapods_org_gh_repo_owner,
    cocoapods_org_gh_repo_name,
    tag,
    cocoapods_org_pod_name
):
    name = name
    homepage_url = None
    vcs_url = None
    github_url = None
    bug_tracking_url = None
    code_view_url = None
    license_data = None
    declared_license = None
    primary_language = None

    if cocoapods_org_gh_repo_owner and cocoapods_org_gh_repo_name:
        name = cocoapods_org_gh_repo_name
        namespace = cocoapods_org_gh_repo_owner
        base_path = "https://api.github.com/repos"
        api_url = f"{base_path}/{namespace}/{name}"
        gh_repo_api_response = utils.get_github_rest_no_exception(api_url)

        if "Failed to fetch" not in gh_repo_api_response:
            homepage_url = gh_repo_api_response.get("homepage")
            vcs_url = gh_repo_api_response.get("git_url")
            license_data = gh_repo_api_response.get("license") or {}
            declared_license = license_data.get("spdx_id")
            primary_language = gh_repo_api_response.get("language")

        github_url = "https://github.com"
        bug_tracking_url = f"{github_url}/{namespace}/{name}/issues"
        code_view_url = f"{github_url}/{namespace}/{name}"

    corrected_name = cocoapods_org_pod_name
    podspec_api_url = f"https://raw.githubusercontent.com/CocoaPods/Specs/master/Specs/{hashed_path}/{corrected_name}/{tag}/{corrected_name}.podspec.json"
    podspec_api_response = utils.get_json_response(podspec_api_url)

    if "Failed to fetch" in podspec_api_response:
        logger.error(f"{podspec_api_response}")
        print(f"{podspec_api_response}")
        return

    homepage_url = podspec_api_response.get("homepage")

    lic = podspec_api_response.get("license")
    extracted_license_statement = None
    if isinstance(lic, dict):
        extracted_license_statement = lic
    else:
        extracted_license_statement = lic
    if not declared_license:
        declared_license = extracted_license_statement

    source = podspec_api_response.get("source")
    vcs_url = None
    download_url = None
    if isinstance(source, dict):
        git_url = source.get("git", "")
        http_url = source.get("http", "")
        if http_url:
            download_url = http_url
        if git_url and not http_url:
            if git_url.endswith(".git") and "github" in git_url:
                gh_path = git_url[:-4]
                corrected_tag = tag
                if source.get("tag") and source.get("tag").startswith("v"):
                    corrected_tag = source.get("tag")
                download_url = f"{gh_path}/archive/refs/tags/{corrected_tag}.tar.gz"
                vcs_url = git_url
        elif git_url:
            vcs_url = git_url
    elif isinstance(source, str):
        if not vcs_url:
            vcs_url = source

    purl_pkg = Package(
        homepage_url=homepage_url,
        api_url=podspec_api_url,
        bug_tracking_url=bug_tracking_url,
        code_view_url=code_view_url,
        download_url=download_url,
        declared_license=declared_license,
        primary_language=primary_language,
        repository_homepage_url=repository_homepage_url,
        vcs_url=vcs_url,
        **purl.to_dict(),
    )
    purl_pkg.version = tag
    return purl_pkg
