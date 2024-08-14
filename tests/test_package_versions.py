# fetchcode is a free software tool from nexB Inc. and others.
# Visit https://github.com/aboutcode-org/fetchcode for support and download.

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
from pathlib import Path
from unittest import mock

import yaml

from fetchcode.package_versions import versions

FETCHCODE_REGEN_TEST_FIXTURES = os.getenv(
    "FETCHCODE_REGEN_TEST_FIXTURES", False)

data_location = Path(__file__).parent / "data" / "package_versions"


def get_json_data(file):
    with file.open(encoding="utf-8") as f:
        return json.load(f)


def check_results_against_json(
    result,
    expected_file,
    regen=FETCHCODE_REGEN_TEST_FIXTURES,
):
    expected_data = get_json_data(expected_file)
    result_dict = [i.to_dict() for i in result]
    if regen:
        with expected_file.open(encoding="utf-8", mode="w") as f:
            json.dump(result_dict, f, indent=4)

    assert all([a in result_dict for a in expected_data])


@mock.patch("fetchcode.package_versions.get_response")
def test_get_launchpad_versions_from_purl(mock_get_response):
    side_effect = [get_json_data(data_location / "launchpad_mock_data.json")]
    purl = "pkg:deb/ubuntu/dpkg"
    expected_file = data_location / "launchpad.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_pypi_versions_from_purl(mock_get_response):
    side_effect = [get_json_data(data_location / "pypi_mock_data.json")]
    purl = "pkg:pypi/django"
    expected_file = data_location / "pypi.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_cargo_versions_from_purl(mock_get_response):
    side_effect = [get_json_data(data_location / "cargo_mock_data.json")]
    purl = "pkg:cargo/yprox"
    expected_file = data_location / "cargo.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_gem_versions_from_purl(mock_get_response):
    side_effect = [get_json_data(data_location / "gem_mock_data.json")]
    purl = "pkg:gem/ruby-advisory-db-check"
    expected_file = data_location / "gem.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_npm_versions_from_purl(mock_get_response):
    side_effect = [get_json_data(data_location / "npm_mock_data.json")]
    purl = "pkg:npm/%40angular/animation"
    expected_file = data_location / "npm.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_deb_versions_from_purl(mock_get_response):
    side_effect = [get_json_data(data_location / "deb_mock_data.json")]
    purl = "pkg:deb/debian/attr"
    expected_file = data_location / "deb.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_maven_versions_from_purl(mock_get_response):
    maven_mock_file = data_location / "maven_mock_data.xml"
    with maven_mock_file.open(mode="rb") as f:
        data = f.read()

    side_effect = [data]
    purl = "pkg:maven/org.apache.xmlgraphics/batik-anim"
    expected_file = data_location / "maven.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_nuget_versions_from_purl(mock_get_response):
    side_effect = [get_json_data(data_location / "nuget_mock_data.json")]
    purl = "pkg:nuget/EnterpriseLibrary.Common"
    expected_file = data_location / "nuget.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_composer_versions_from_purl(mock_get_response):
    side_effect = [get_json_data(data_location / "composer_mock_data.json")]
    purl = "pkg:composer/laravel/laravel"
    expected_file = data_location / "composer.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_hex_versions_from_purl(mock_get_response):
    side_effect = [get_json_data(data_location / "hex_mock_data.json")]
    purl = "pkg:hex/jason"
    expected_file = data_location / "hex.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_conan_versions_from_purl(mock_get_response):
    with open(data_location / "conan_mock_data.yml", "r") as file:
        data = yaml.safe_load(file)

    side_effect = [data]
    purl = "pkg:conan/openssl"
    expected_file = data_location / "conan.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.utils.github_response")
def test_get_github_versions_from_purl(mock_github_response):
    github_mock_directory = data_location / "github"
    side_effect = []
    sorted_version_files = sorted(github_mock_directory.glob("*.json"))
    for path in sorted_version_files:
        side_effect.append(get_json_data(path))

    purl = "pkg:github/nexB/scancode-toolkit"
    expected_file = data_location / "github.json"
    mock_github_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)


@mock.patch("fetchcode.package_versions.get_response")
def test_get_golang_versions_from_purl(mock_get_response):
    golang_version_list_file = data_location / "golang/golang_mock_meta_data.txt"
    side_effect = []
    with golang_version_list_file.open(encoding="utf-8") as f:
        version_list = f.read()
        side_effect.append(version_list)

    for version in version_list.split():
        side_effect.append(
            get_json_data(
                data_location /
                f"golang/versions/golang_mock_{version}_data.json"
            )
        )

    purl = "pkg:golang/github.com/blockloop/scan"
    expected_file = data_location / "golang.json"
    mock_get_response.side_effect = side_effect
    result = list(versions(purl))
    check_results_against_json(result, expected_file)
