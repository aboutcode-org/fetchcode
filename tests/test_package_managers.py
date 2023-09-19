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
from unittest import mock

from fetchcode.package_managers import versions


def file_data(file_name):
    with open(file_name) as file:
        data = file.read()
        return json.loads(data)


def match_data(result, expected_file):
    expected_data = file_data(expected_file)
    result_dict = [i.to_dict() for i in result]
    assert result_dict == expected_data


@mock.patch("fetchcode.package_managers.get_response")
def test_get_launchpad_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_managers/launchpad_mock_data.json")]
    purl = "pkg:deb/ubuntu/dpkg"
    expected_file = "tests/data/package_managers/launchpad.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_pypi_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_managers/pypi_mock_data.json")]
    purl = "pkg:pypi/django"
    expected_file = "tests/data/package_managers/pypi.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_cargo_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_managers/cargo_mock_data.json")]
    purl = "pkg:cargo/yprox"
    expected_file = "tests/data/package_managers/cargo.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_gem_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_managers/gem_mock_data.json")]
    purl = "pkg:gem/ruby-advisory-db-check"
    expected_file = "tests/data/package_managers/gem.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_npm_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_managers/npm_mock_data.json")]
    purl = "pkg:npm/%40angular/animation"
    expected_file = "tests/data/package_managers/npm.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_deb_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_managers/deb_mock_data.json")]
    purl = "pkg:deb/debian/attr"
    expected_file = "tests/data/package_managers/deb.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_maven_versions_from_purl(mock_get_response):
    with open("tests/data/package_managers/maven_mock_data.xml", "rb") as file:
        data = file.read()

    side_effect = [data]
    purl = "pkg:maven/org.apache.xmlgraphics/batik-anim"
    expected_file = "tests/data/package_managers/maven.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_nuget_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_managers/nuget_mock_data.json")]
    purl = "pkg:nuget/EnterpriseLibrary.Common"
    expected_file = "tests/data/package_managers/nuget.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_composer_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_managers/composer_mock_data.json")]
    purl = "pkg:composer/laravel/laravel"
    expected_file = "tests/data/package_managers/composer.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_hex_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_managers/hex_mock_data.json")]
    purl = "pkg:hex/jason"
    expected_file = "tests/data/package_managers/hex.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_conan_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_managers/conan_mock_data.json")]
    purl = "pkg:conan/openssl"
    expected_file = "tests/data/package_managers/conan.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_github_versions_from_purl(mock_get_response):
    side_effect = [file_data("tests/data/package_managers/github_mock_data.json")]
    purl = "pkg:github/nexB/scancode-toolkit"
    expected_file = "tests/data/package_managers/github.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)


@mock.patch("fetchcode.package_managers.get_response")
def test_get_golang_versions_from_purl(mock_get_response):
    side_effect = [
        "v1.3.0\nv1.0.0\nv1.1.1\nv1.2.1\nv1.2.0\nv1.1.0\n",
        {"Version": "v1.3.0", "Time": "2019-04-19T01:47:04Z"},
        {"Version": "v1.0.0", "Time": "2018-02-22T03:48:05Z"},
        {"Version": "v1.1.1", "Time": "2018-02-25T16:25:39Z"},
        {"Version": "v1.2.1", "Time": "2018-03-01T05:21:19Z"},
        {"Version": "v1.2.0", "Time": "2018-02-25T19:58:02Z"},
        {"Version": "v1.1.0", "Time": "2018-02-24T22:49:07Z"},
    ]
    purl = "pkg:golang/github.com/blockloop/scan"
    expected_file = "tests/data/package_managers/golang.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    match_data(result, expected_file)
