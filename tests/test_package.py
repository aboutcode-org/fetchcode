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

from fetchcode.package import info


def file_data(file_name):
    with open(file_name) as file:
        data = file.read()
        return json.loads(data)


@mock.patch("fetchcode.package.get_response")
def test_packages(mock_get):

    package_managers = {
        "cargo": {
            "side_effect": [file_data("tests/data/cargo_mock_data.json")],
            "purl": "pkg:cargo/rand",
            "expected_data": "tests/data/cargo.json",
        },
        "npm": {
            "side_effect": [file_data("tests/data/npm_mock_data.json")],
            "purl": "pkg:npm/express",
            "expected_data": "tests/data/npm.json",
        },
        "pypi": {
            "side_effect": [file_data("tests/data/pypi_mock_data.json")],
            "purl": "pkg:pypi/flask",
            "expected_data": "tests/data/pypi.json",
        },
        "github": {
            "side_effect": [
                file_data("tests/data/github_mock_data.json"),
                file_data("tests/data/github_mock_release_data.json"),
            ],
            "purl": "pkg:github/TG1999/fetchcode",
            "expected_data": "tests/data/github.json",
        },
        "bitbucket": {
            "side_effect": [
                file_data("tests/data/bitbucket_mock_data.json"),
                file_data("tests/data/bitbucket_mock_release_data.json"),
            ],
            "purl": "pkg:bitbucket/litmis/python-itoolkit",
            "expected_data": "tests/data/bitbucket.json",
        },
        "rubygems": {
            "side_effect": [file_data("tests/data/rubygems_mock_data.json")],
            "purl": "pkg:rubygems/rubocop",
            "expected_data": "tests/data/rubygems.json",
        },
    }

    for package_manager in package_managers.values():
        mock_get.side_effect = package_manager["side_effect"]
        packages = list(info(package_manager["purl"]))
        data = [dict(p.to_dict()) for p in packages]
        expected_data_dict = file_data(package_manager["expected_data"])
        expected_data = [dict(expected_data_dict[p]) for p in expected_data_dict]
        assert expected_data == data
