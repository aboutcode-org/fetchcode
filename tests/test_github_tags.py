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

from package_registry import github_tags


@mock.patch('package_registry.github_tags.requests.get')
def test_github_tags_for_not_empty_list(mock_get):
    url = 'https://github.com/nexb/scancode-toolkit'
    with open('tests/data/gh_tags_response.json') as file:
        data = file.read()
    mock_get.return_value.json.return_value = json.loads(data)
    response = github_tags.get_tags(url=url)
    tags = ['v3.1.1', 'v3.1.0', 'v3.0.2', 'v3.0.1', 'v3.0.0', 'v2.9.9', 'v2.9.8', 'v2.9.7', 'v2.9.6', 'v2.9.5', 'v2.9.4', 'v2.9.3', 'v2.9.2', 'v2.9.1', 'v2.9.0b1', 'v2.2.1', 'v2.2.0', 'v2.1.0', 'v2.0.1', 'v2.0.0', 'v2.0.0.rc3', 'v2.0.0.rc2', 'v2.0.0.rc1', 'v1.6.3', 'v1.6.2', 'v1.6.1', 'v1.6.0', 'v1.5.0', 'v1.4.3', 'v1.4.2']
    for tag in tags:
        assert tag in response
    assert 'v5.0.1' not in response

@mock.patch('package_registry.github_tags.requests.get')
def test_github_tags_for_empty_list(mock_get):
    mock_get.return_value.json.return_value=[]
    url = 'https://github.com/nexb/fetchcode'
    response = github_tags.get_tags(url=url)
    assert 0 == len(response)

def test_build_url_with_conventional_URL():
    url = 'https://github.com/nexb/fetchcode'
    excepted = 'https://api.github.com/repos/nexb/fetchcode/tags'
    final_url = github_tags.build_url(url)
    assert excepted == final_url 

def test_build_url_with_unconventional_URL():
    url = 'https://github.com/nexB/fetchcode/tree/master'
    excepted = 'https://api.github.com/repos/nexB/fetchcode/tags'
    final_url = github_tags.build_url(url)
    assert excepted == final_url 
