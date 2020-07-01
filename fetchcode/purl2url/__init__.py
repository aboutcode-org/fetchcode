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

from urllib.parse import urlparse


def index_in_list(index, list):
    return index < len(list)


def build_bitbucket(**data):
    """
    Take dictionary `data` as input and returns a valid bitbucket URL string `url` 
    """

    name = data["name"]
    namespace = data["namespace"]
    if not (name and namespace):
        return

    url = "https://bitbucket.org/{namespace}/{name}".format(
        namespace=namespace, name=name
    )
    version = data["version"]
    if version:
        url = "{url}/src/{version}".format(url=url, version=version)

    subpath = data["subpath"]
    if subpath:
        url = "{url}/{subpath}".format(url=url, subpath=subpath)

    return url


def build_cargo(**data):
    """
    Take dictionary `data` as input and returns a valid cargo URL string `url`
    """
    name = data["name"]
    version = data["version"]
    if not (name and version):
        return

    return "https://crates.io/api/v1/crates/{name}/{version}/download".format(
        name=name, version=version
    )


def build_github(**data):
    """
    Take dictionary `data` as input and returns a valid github URL string `url`
    """
    name = data["name"]
    namespace = data["namespace"]
    if not (name and namespace):
        return

    url = "https://github.com/{namespace}/{name}".format(namespace=namespace, name=name)

    version = data["version"]
    if version:
        url = "{url}/tree/{version}".format(url=url, version=version)

    subpath = data["subpath"]
    if subpath:
        url = "{url}/{subpath}".format(url=url, subpath=subpath)

    return url


def build_gitlab(**data):
    """
    Take dictionary `data` as input and returns a valid gitlab URL string `url`
    """
    name = data["name"]
    namespace = data["namespace"]

    if not (name and namespace):
        return

    url = "https://gitlab.com/{namespace}/{name}".format(namespace=namespace, name=name)

    version = data["version"]
    if version:
        url = "{url}/-/tree/{version}".format(url=url, version=version)

    subpath = data["subpath"]
    if subpath:
        url = "{url}/{subpath}".format(url=url, subpath=subpath)

    return url


def build_gem(**data):
    """
    Take dictionary `data` as input and returns a valid rubygem URL string `url`
    """
    name = data["name"]
    version = data["version"]

    if not (name and version):
        return

    return "https://rubygems.org/downloads/{name}-{version}.gem".format(
        name=name, version=version
    )


def purl2url(purl):
    """
    Take PackageURL `purl` as input and return a valid URL string `url` depending on the type of purl 
    """
    url_parts = urlparse(purl)

    subpath = url_parts.fragment if url_parts.fragment != "" else None
    qualifiers = url_parts.query if url_parts.query != "" else None

    path = url_parts.path
    path = path.split("@")

    if index_in_list(1, path):
        version = path[1]
    else:
        version = None

    path = path[0]

    path = path.split("/")

    name = None
    namespace = None

    # pkg:github/TG1999/fetchcode
    if index_in_list(2, path):
        name = path[2]
        namespace = path[1]

    # pkg:crago/clap@2.3.3
    elif index_in_list(1, path):
        name = path[1]

    type = path[0]

    converter = {
        "bitbucket": build_bitbucket,
        "cargo": build_cargo,
        "gem": build_gem,
        "github": build_github,
        "gitlab": build_gitlab,
    }

    if type in converter:
        url = converter[type](
            name=name,
            namespace=namespace,
            version=version,
            qualifiers=qualifiers,
            subpath=subpath,
        )
        return url
