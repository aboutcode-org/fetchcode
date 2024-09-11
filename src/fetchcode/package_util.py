# fetchcode is a free software tool from nexB Inc. and others.
# Visit https://github.com/aboutcode-org/fetchcode for support and download.
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
import json
import re
from pathlib import Path

import attr

from fetchcode import utils
from fetchcode.packagedcode_models import Package

DATA = Path(__file__).parent / "data"


def package_from_dict(package_data):
    """
    Return a Package built from a `package_data` mapping.
    Ignore unknown and unsupported fields.
    """
    supported = {attr.name for attr in attr.fields(Package)}
    cleaned_package_data = {key: value for key, value in package_data.items() if key in supported}
    return Package(**cleaned_package_data)


@dataclasses.dataclass
class GitHubSource:
    version_regex: re.Pattern = dataclasses.field(
        default=None,
        metadata={"help_text": "Regular expression pattern to match and extract version from tag."},
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
    for package in _get_github_packages(purl, version_regex, ignored_tag_regex, default_package):
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
    archive_download_url = "https://github.com/{org}/{name}/archive/refs/tags/{tag_name}.tar.gz"

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

        download_url = archive_download_url.format(org=purl.namespace, name=purl.name, tag_name=tag)

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
        cls.version_regex = re.compile(cls.version_regex_template.format(re.escape(package_name)))

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
UDHCP_RELEASES = json.loads((DATA / "udhcp_releases.json").read_text(encoding="UTF-8"))


# Since there will be no new releases of ipkg, it's better to
# store them in a dictionary rather than fetching them every time.
IPKG_RELEASES = json.loads((DATA / "ipkg_releases.json").read_text(encoding="UTF-8"))
