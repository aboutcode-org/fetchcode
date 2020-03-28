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

import json
from unittest import mock

from package_registry import rust_versions


@mock.patch('package_registry.rust_versions.requests.get')
def test_rust_versions_for_not_empty_list(mock_get):
    package = 'rand'
    with open('tests/data/rust_versions_response.json') as file:
        data = file.read()
    mock_get.return_value.json.return_value = json.loads(data)
    response = rust_versions.get_versions(package=package)
    tags = ['0.7.3', '0.7.2', '0.7.1', '0.7.0', '0.7.0-pre.2', '0.7.0-pre.1', '0.7.0-pre.0', '0.6.5', '0.6.4', '0.6.3', '0.6.2', '0.6.1', '0.6.0', '0.6.0-pre.1', '0.6.0-pre.0', '0.5.6', '0.5.5', '0.5.4', '0.5.3', '0.5.2', '0.5.1', '0.5.0', '0.5.0-pre.2', '0.5.0-pre.1', '0.5.0-pre.0', '0.4.6', '0.4.5', '0.4.4', '0.4.3', '0.4.2', '0.4.1', '0.4.0-pre.0', '0.3.23', '0.3.22', '0.3.21-pre.0', '0.3.20', '0.3.19', '0.3.18', '0.3.17', '0.3.16', '0.3.15', '0.3.14', '0.3.13', '0.3.12', '0.3.11', '0.3.10', '0.3.9', '0.3.8', '0.3.7', '0.3.6', '0.3.5', '0.3.4', '0.3.3', '0.3.2', '0.3.1', '0.3.0', '0.2.1', '0.2.0', '0.1.4', '0.1.3', '0.1.2', '0.1.1']
    for tag in tags:
        assert tag in response
    assert '0.7.9' not in response

def test_build_url():
    package = 'libc'
    expected = 'https://crates.io/api/v1/crates/libc'
    url = rust_versions.build_url(package=package)
    assert expected == url 

@mock.patch('package_registry.rust_versions.requests.get')
def test_rust_version_with_None(mock_get):
    package = None
    mock_get.return_value.json.return_value = {'errors': [{'detail': 'Not Found'}]}
    response = rust_versions.get_versions(package=package)
    assert [] == response

@mock.patch('package_registry.rust_versions.requests.get')
def test_rust_version_with_empty_package_name(mock_get):
    package = ''
    mock_get.return_value.json.return_value = {'errors': [{'detail': 'Not Found'}]}
    response = rust_versions.get_versions(package=package)
    assert [] == response

@mock.patch('package_registry.rust_versions.requests.get')
def test_rust_version_with_junk_package_name(mock_get):
    package = '!@#$%^*&*()"ABCD1234'
    mock_get.return_value.json.return_value = {'errors': [{'detail': 'Not Found'}]}
    response = rust_versions.get_versions(package=package)
    assert [] == response
