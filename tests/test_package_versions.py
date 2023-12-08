# fetchcode is a free software tool from nexB Inc. and others.
# Visit https://github.com/nexB/fetchcode for support and download.

# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and http://aboutcode.org

# This software is licensed under the Apache License version 2.0.

# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at:
# http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json
import os
from unittest import mock

import yaml

from fetchcode.package_versions import versions

FETCHCODE_REGEN_TEST_FIXTURES = os.getenv("FETCHCODE_REGEN_TEST_FIXTURES", False)


def file_data(file_name):
    with open(file_name) as file:
        data = file.read()
        return json.loads(data)


def match_data(
    result,
    expected_file,
    regen=FETCHCODE_REGEN_TEST_FIXTURES,
):
    expected_data = file_data(expected_file)
    result_dict = [i.to_dict() for i in result]
    if regen:
        with open(expected_file, "w") as file:
            json.dump(result_dict, file, indent=4)

    assert all([a in result_dict for a in expected_data])


@mock.patch("fetchcode.package_versions.get_response")
def test_get_launchpad_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_versions/launchpad_mock_data.json")]
    purl = "pkg:deb/ubuntu/dpkg"
    expected_file = "tests/data/package_versions/launchpad.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_pypi_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_versions/pypi_mock_data.json")]
    purl = "pkg:pypi/django"
    expected_file = "tests/data/package_versions/pypi.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_cargo_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_versions/cargo_mock_data.json")]
    purl = "pkg:cargo/yprox"
    expected_file = "tests/data/package_versions/cargo.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_gem_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_versions/gem_mock_data.json")]
    purl = "pkg:gem/ruby-advisory-db-check"
    expected_file = "tests/data/package_versions/gem.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_npm_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_versions/npm_mock_data.json")]
    purl = "pkg:npm/%40angular/animation"
    expected_file = "tests/data/package_versions/npm.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_deb_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_versions/deb_mock_data.json")]
    purl = "pkg:deb/debian/attr"
    expected_file = "tests/data/package_versions/deb.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_maven_versions_from_purl(mock_get_response):
    with open("tests/data/package_versions/maven_mock_data.xml", "rb") as file:
        data = file.read()

    side_effect = [data]
    purl = "pkg:maven/org.apache.xmlgraphics/batik-anim"
    expected_file = "tests/data/package_versions/maven.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_nuget_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_versions/nuget_mock_data.json")]
    purl = "pkg:nuget/EnterpriseLibrary.Common"
    expected_file = "tests/data/package_versions/nuget.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_composer_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_versions/composer_mock_data.json")]
    purl = "pkg:composer/laravel/laravel"
    expected_file = "tests/data/package_versions/composer.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_hex_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_versions/hex_mock_data.json")]
    purl = "pkg:hex/jason"
    expected_file = "tests/data/package_versions/hex.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_conan_versions_from_purl(mock_get_response):
    with open("tests/data/package_versions/conan_mock_data.yml", "r") as file:
        data = yaml.safe_load(file)

    side_effect = [data]
    purl = "pkg:conan/openssl"
    expected_file = "tests/data/package_versions/conan.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


# @mock.patch("fetchcode.package_versions.github_response")
# def test_get_github_versions_from_purl(mock_github_response):
#     side_effect = [file_data("tests/data/package_versions/github_mock_data.json")]
#     purl = "pkg:github/nexB/scancode-toolkit"
#     expected_file = "tests/data/package_versions/github.json"
#     mock_github_response.side_effect = side_effect
#     result = list(versions(purl))
#     match_data(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_golang_versions_from_purl(mock_get_response):
    golang_version_list_file = (
        "tests/data/package_versions/golang/golang_mock_meta_data.txt"
    )
    side_effect = []
    with open(golang_version_list_file, "r") as file:
        version_list = file.read()
        side_effect.append(version_list)

    for version in version_list.split():
        version_file = f"tests/data/package_versions/golang/versions/golang_mock_{version}_data.json"
        side_effect.append(file_data(version_file))

    purl = "pkg:golang/github.com/blockloop/scan"
    expected_file = "tests/data/package_versions/golang.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)
