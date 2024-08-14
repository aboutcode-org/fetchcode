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
import logging
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Iterable
from typing import Optional
from urllib.parse import urlparse

import requests
import yaml
from dateutil import parser as dateparser
from packageurl import PackageURL
from packageurl.contrib.route import NoRouteAvailable
from packageurl.contrib.route import Router

from fetchcode.utils import fetch_github_tags_gql

logger = logging.getLogger(__name__)

router = Router()

SUPPORTED_ECOSYSTEMS = [
    "cargo",
    "composer",
    "conan",
    "deb",
    "gem",
    "github",
    "golang",
    "hex",
    "maven",
    "npm",
    "nuget",
    "pypi",
]


def versions(purl):
    """Return all version for a PURL."""
    if purl:
        try:
            return router.process(purl)
        except NoRouteAvailable:
            return


@dataclasses.dataclass(frozen=True)
class PackageVersion:
    value: str
    release_date: Optional[datetime] = None

    def to_dict(self):
        release_date = self.release_date
        release_date = release_date and release_date.isoformat()
        return dict(value=self.value, release_date=release_date)


@router.route("pkg:deb/ubuntu/.*")
def get_launchpad_versions_from_purl(purl):
    """Fetch versions of Ubuntu debian packages from Launchpad."""
    purl = PackageURL.from_string(purl)
    url = (
        f"https://api.launchpad.net/1.0/ubuntu/+archive/primary?"
        f"ws.op=getPublishedSources&source_name={purl.name}&exact_match=true"
    )

    while True:
        response = get_response(url=url, content_type="json")

        if not response:
            break
        entries = response.get("entries")
        if not entries:
            break

        for release in entries:
            source_package_version = release.get("source_package_version")
            source_package_version = remove_debian_default_epoch(
                version=source_package_version
            )
            date_published = release.get("date_published")
            release_date = None
            if date_published and type(date_published) is str:
                release_date = dateparser.parse(date_published)
            if source_package_version:
                yield PackageVersion(
                    value=source_package_version,
                    release_date=release_date,
                )

        next_collection_link = response.get("next_collection_link")
        if next_collection_link:
            url = next_collection_link
        else:
            break


@router.route("pkg:pypi/.*")
def get_pypi_versions_from_purl(purl):
    """Fetch versions of Python pypi packages from the PyPI API."""
    purl = PackageURL.from_string(purl)
    response = get_response(url=f"https://pypi.org/pypi/{purl.name}/json")
    if not response:
        return

    releases = response.get("releases") or {}
    for version, download_items in releases.items():
        if not download_items:
            continue

        release_date = get_pypi_latest_date(download_items)
        yield PackageVersion(
            value=version,
            release_date=release_date,
        )


@router.route("pkg:cargo/.*")
def get_cargo_versions_from_purl(purl):
    """Fetch versions of Rust cargo packages from the crates.io API."""
    purl = PackageURL.from_string(purl)
    url = f"https://crates.io/api/v1/crates/{purl.name}"
    response = get_response(
        url=url, content_type="json", headers={"User-Agent": "pm_bot"}
    )

    for version_info in response.get("versions"):
        yield PackageVersion(
            value=version_info["num"],
            release_date=dateparser.parse(version_info["updated_at"]),
        )


@router.route("pkg:gem/.*")
def get_gem_versions_from_purl(purl):
    """Fetch versions of Rubygems packages from the rubygems API."""
    purl = PackageURL.from_string(purl)
    url = f"https://rubygems.org/api/v1/versions/{purl.name}.json"
    response = get_response(url=url, content_type="json")
    if not response:
        return
    for release in response:
        published_at = release.get("published_at")
        created_at = release.get("created_at")
        number = release.get("number")
        release_date = None

        if published_at:
            release_date = dateparser.parse(published_at)
        elif created_at:
            release_date = dateparser.parse(created_at)

        if number:
            yield PackageVersion(value=number, release_date=release_date)
        else:
            logger.error(f"Failed to parse release {release} from url: {url}")


@router.route("pkg:npm/.*")
def get_npm_versions_from_purl(purl):
    """Fetch versions of npm packages from the npm registry API."""
    purl = PackageURL.from_string(purl)
    url = f"https://registry.npmjs.org/{purl.name}"
    response = get_response(url=url, content_type="json")
    if not response:
        logger.error(f"Failed to fetch {url}")
        return
    for version in response.get("versions") or []:
        release_date = response.get("time", {}).get(version)
        release_date = release_date and dateparser.parse(release_date) or None
        yield PackageVersion(value=version, release_date=release_date)


@router.route("pkg:deb/debian/.*")
def get_deb_versions_from_purl(purl):
    """
    Fetch versions of Debian debian packages from the sources.debian.org API.
    """
    purl = PackageURL.from_string(purl)
    # Need to set the headers, because the Debian API upgrades
    # the connection to HTTP 2.0
    response = get_response(
        url=f"https://sources.debian.org/api/src/{purl.name}",
        headers={"Connection": "keep-alive"},
        content_type="json",
    )
    if response and (response.get("error") or not response.get("versions")):
        return

    for release in response["versions"]:
        version = release["version"]
        version = remove_debian_default_epoch(version)
        yield PackageVersion(value=version)


@router.route("pkg:maven/.*")
def get_maven_versions_from_purl(purl):
    """Fetch versions of Maven packages from Maven Central maven-metadata.xml data."""
    purl = PackageURL.from_string(purl)
    group_id = purl.namespace
    artifact_id = purl.name
    if not group_id:
        return

    group_url = group_id.replace(".", "/")
    endpoint = (
        f"https://repo1.maven.org/maven2/{group_url}/{artifact_id}/maven-metadata.xml"
    )
    response = get_response(url=endpoint, content_type="binary")
    if response:
        xml_resp = ET.ElementTree(ET.fromstring(response.decode("utf-8")))
        yield from maven_extract_versions(xml_resp)


@router.route("pkg:nuget/.*")
def get_nuget_versions_from_purl(purl):
    """Fetch versions of NuGet packages from the nuget.org API."""
    purl = PackageURL.from_string(purl)
    pkg = purl.name.lower()
    url = f"https://api.nuget.org/v3/registration5-semver1/{pkg}/index.json"
    resp = get_response(url=url)
    if resp:
        yield from nuget_extract_versions(resp)


@router.route("pkg:composer/.*")
def get_composer_versions_from_purl(purl):
    """Fetch versions of PHP Composer packages from the packagist.org API."""
    purl = PackageURL.from_string(purl)
    if not purl.namespace:
        return

    pkg = f"{purl.namespace}/{purl.name}"
    response = get_response(url=f"https://repo.packagist.org/p/{pkg}.json")
    if response:
        yield from composer_extract_versions(response, pkg)


@router.route("pkg:hex/.*")
def get_hex_versions_from_purl(purl):
    """Fetch versions of Erlang packages from the hex API."""
    purl = PackageURL.from_string(purl)
    response = get_response(
        url=f"https://hex.pm/api/packages/{purl.name}",
        content_type="json",
    )
    for release in response["releases"]:
        yield PackageVersion(
            value=release["version"],
            release_date=dateparser.parse(release["inserted_at"]),
        )


@router.route("pkg:conan/.*")
def get_conan_versions_from_purl(purl):
    """Fetch versions of ``conan`` packages from the Conan API."""
    purl = PackageURL.from_string(purl)
    response = get_response(
        url=(
            "https://raw.githubusercontent.com/conan-io/conan-center-index/"
            f"master/recipes/{purl.name}/config.yml"
        ),
        content_type="yaml",
    )
    for version in response["versions"].keys():
        yield PackageVersion(value=version)


@router.route("pkg:github/.*")
def get_github_versions_from_purl(purl):
    """Fetch versions of ``github`` packages using GitHub REST API."""
    purl = PackageURL.from_string(purl)

    for version, date in fetch_github_tags_gql(purl):
        yield PackageVersion(value=version, release_date=date)


@router.route("pkg:golang/.*")
def get_golang_versions_from_purl(purl):
    """Fetch versions of Go "golang" packages from the Go proxy API."""
    purl = PackageURL.from_string(purl)
    package_slug = f"{purl.namespace}/{purl.name}"
    # escape uppercase in module path
    escaped_pkg = escape_path(package_slug)
    trimmed_pkg = package_slug
    response = None
    # resolve module name from package name, see https://go.dev/ref/mod#resolve-pkg-mod
    while escaped_pkg is not None:
        url = f"https://proxy.golang.org/{escaped_pkg}/@v/list"
        response = get_response(url=url, content_type="text")
        if not response:
            trimmed_escaped_pkg = trim_go_url_path(escaped_pkg)
            trimmed_pkg = trim_go_url_path(trimmed_pkg) or ""
            if trimmed_escaped_pkg == escaped_pkg:
                break

            escaped_pkg = trimmed_escaped_pkg
            continue

        break

    if response is None or escaped_pkg is None or trimmed_pkg is None:
        logger.error(
            f"Error while fetching versions for {package_slug!r} from goproxy")
        return

    for version_info in response.split("\n"):
        version = fetch_version_info(version_info, escaped_pkg)
        if version:
            yield version


def trim_go_url_path(url_path: str) -> Optional[str]:
    """
    Return a trimmed Go `url_path` removing trailing
    package references and keeping only the module
    references.

    Github advisories for Go are using package names
    such as "https://github.com/nats-io/nats-server/v2/server"
    (e.g., https://github.com/advisories/GHSA-jp4j-47f9-2vc3 ),
    yet goproxy works with module names instead such as
    "https://github.com/nats-io/nats-server" (see for details
    https://golang.org/ref/mod#goproxy-protocol ).
    This functions trims the trailing part(s) of a package URL
    and returns the remaining the module name.
    For example:
    >>> module = "github.com/xx/a"
    >>> assert trim_go_url_path("https://github.com/xx/a/b") == module
    """
    # some advisories contains this prefix in package name, e.g. https://github.com/advisories/GHSA-7h6j-2268-fhcm
    go_url_prefix = "https://pkg.go.dev/"
    if url_path.startswith(go_url_prefix):
        url_path = url_path[len(go_url_prefix):]

    parsed_url_path = urlparse(url_path)
    path = parsed_url_path.path
    parts = path.split("/")
    if len(parts) < 3:
        logger.error(f"Not a valid Go URL path {url_path} trim_go_url_path")
        return
    else:
        joined_path = "/".join(parts[:3])
        return f"{parsed_url_path.netloc}{joined_path}"


def escape_path(path: str) -> str:
    """
    Return an case-encoded module path or version name.

    This is done by replacing every uppercase letter with an exclamation
    mark followed by the corresponding lower-case letter, in order to
    avoid ambiguity when serving from case-insensitive file systems.
    Refer to https://golang.org/ref/mod#goproxy-protocol.
    """
    escaped_path = ""
    for c in path:
        if c >= "A" and c <= "Z":
            # replace uppercase with !lowercase
            escaped_path += "!" + chr(ord(c) + ord("a") - ord("A"))
        else:
            escaped_path += c
    return escaped_path


def fetch_version_info(version_info: str, escaped_pkg: str) -> Optional[PackageVersion]:
    # Example version_info:
    #     "v1.3.0 2019-04-19T01:47:04Z"
    #     "v1.3.0"
    version_parts = version_info.split()
    if not version_parts:
        return

    # Extract version and date if available
    version = version_parts[0]
    date = version_parts[1] if len(version_parts) > 1 else None

    if date:
        # get release date from the second part. see
        # https://github.com/golang/go/blob/ac02fdec7cd16ea8d3de1fc33def9cfabec5170d/src/cmd/go/internal/modfetch/proxy.go#L136-L147

        release_date = dateparser.parse(date)
    else:
        escaped_ver = escape_path(version)
        response = get_response(
            url=f"https://proxy.golang.org/{escaped_pkg}/@v/{escaped_ver}.info",
            content_type="json",
        )

        if not response:
            logger.error(
                f"Error while fetching version info for {escaped_pkg}/{escaped_ver} "
                f"from goproxy:\n{traceback.format_exc()}"
            )
        release_date = dateparser.parse(
            response.get("Time", "")) if response else None

    return PackageVersion(value=version, release_date=release_date)


def composer_extract_versions(resp: dict, pkg: str) -> Iterable[PackageVersion]:
    for version in get_item(resp, "packages", pkg) or []:
        if "dev" in version:
            continue

        # This if statement ensures, that all_versions contains only released versions
        # See https://github.com/composer/composer/blob/44a4429978d1b3c6223277b875762b2930e83e8c/doc/articles/versions.md#tags  # nopep8
        # for explanation of removing 'v'
        time = get_item(resp, "packages", pkg, version, "time")
        yield PackageVersion(
            value=cleaned_version(version),
            release_date=dateparser.parse(time) if time else None,
        )


def get_item(dictionary: dict, *attributes):
    """
    Return `item` by going through all the `attributes` present in the `dictionary`.

    Do a DFS for the `item` in the `dictionary` by traversing the `attributes`
    and return None if can not traverse through the `attributes`
    For example:
    >>> get_item({'a': {'b': {'c': 'd'}}}, 'a', 'b', 'c')
    'd'
    >>> assert(get_item({'a': {'b': {'c': 'd'}}}, 'a', 'b', 'e')) == None
    """
    for attribute in attributes:
        if not dictionary:
            return
        if not isinstance(dictionary, dict):
            logger.error("dictionary must be of type `dict`")
            return
        if attribute not in dictionary:
            logger.error(f"Missing attribute {attribute} in {dictionary}")
            return
        dictionary = dictionary[attribute]
    return dictionary


def cleaned_version(version):
    """Return a ``version`` string stripped from leading "v" prefix."""
    return version.lstrip("vV")


def nuget_extract_versions(response: dict) -> Iterable[PackageVersion]:
    for entry_group in response.get("items") or []:
        for entry in entry_group.get("items") or []:
            catalog_entry = entry.get("catalogEntry") or {}
            version = catalog_entry.get("version")
            if not version:
                continue
            release_date = catalog_entry.get("published")
            if release_date:
                release_date = dateparser.parse(release_date)
            yield PackageVersion(
                value=version,
                release_date=release_date,
            )


def maven_extract_versions(
    xml_response: ET.ElementTree,
) -> Iterable[PackageVersion]:
    for child in xml_response.getroot().iter():
        if child.tag == "version" and child.text:
            yield PackageVersion(value=child.text)


def get_pypi_latest_date(downloads):
    """
    Return the latest date from a list of mapping of PyPI ``downloads`` or  None.

    The data has this shape:
    [
      {
        ....
        "upload_time_iso_8601": "2010-12-23T05:14:23.509436Z",
        "url": "https://files.pythonhosted.org/packages/8f/1f/c20ca80fa5df025cc/Django-1.1.3.tar.gz",
      },
      {
        ....
        "upload_time_iso_8601": "2010-12-23T05:20:23.509436Z",
        "url": "https://files.pythonhosted.org/packages/8f/1f/561bddc20ca80fa5df025cc/Django-1.1.3.wheel",
      },
    ]
    """
    latest_date = None
    for download in downloads:
        upload_time = download.get("upload_time_iso_8601")
        if upload_time:
            current_date = dateparser.parse(upload_time)
        if not latest_date:
            latest_date = current_date
        else:
            if current_date > latest_date:
                latest_date = current_date
    return latest_date


def get_response(url, content_type="json", headers=None):
    """
    Fetch ``url`` and return its content as ``content_type`` which is
    one of binary, text, yaml or json.
    """
    try:
        resp = requests.get(url=url, headers=headers)
    except:
        logger.error(traceback.format_exc())
        return
    if not resp.status_code == 200:
        logger.error(f"Error while fetching {url!r}: {resp.status_code!r}")
        return

    if content_type == "binary":
        return resp.content
    elif content_type == "text":
        return resp.text
    elif content_type == "json":
        return resp.json()
    elif content_type == "yaml":
        content = resp.content.decode("utf-8")
        return yaml.safe_load(content)


def remove_debian_default_epoch(version):
    """
    Remove the default epoch from a Debian ``version`` string.

    For Example::
    >>> remove_debian_default_epoch("0:1.2.3-4")
    '1.2.3-4'
    >>> remove_debian_default_epoch("1.2.3-4")
    '1.2.3-4'
    >>> remove_debian_default_epoch(None)
    >>> remove_debian_default_epoch("")
    ''
    """
    return version and version.replace("0:", "")
