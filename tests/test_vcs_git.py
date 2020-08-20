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

from unittest import mock

import pytest

from fetchcode.vcs.git import fetch_via_git


def obtain(dest, url):
    pass


@mock.patch("fetchcode.vcs.git.vcs.get_backend")
def test_fetch_with_git_http_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git+http://github.com/jamesor/mongoose-versioner"
    response = fetch_via_git(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


@mock.patch("fetchcode.vcs.git.vcs.get_backend")
def test_fetch_with_git_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git://github.com/jamesor/mongoose-versioner"
    response = fetch_via_git(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


@mock.patch("fetchcode.vcs.git.vcs.get_backend")
def test_fetch_with_git_https_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git+https://github.com/jamesor/mongoose-versioner"
    response = fetch_via_git(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


@mock.patch("fetchcode.vcs.git.vcs.get_backend")
def test_fetch_with_git_ssh_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git+ssh://github.com/jamesor/mongoose-versioner"
    response = fetch_via_git(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


@mock.patch("fetchcode.vcs.git.vcs.get_backend")
def test_fetch_with_git_file_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git+file://github.com/jamesor/mongoose-versioner"
    response = fetch_via_git(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


@mock.patch("fetchcode.vcs.git.vcs.get_backend")
def test_fetch_with_git_ssh_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git+git://github.com/jamesor/mongoose-versioner"
    response = fetch_via_git(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


def test_fetch_with_git_invalid_scheme():
    invalid_urls = [
        "https://github.com/TG1999/fetchcode",
        "https://bitbucket.org/TG1999/fetchcode",
        "https://gitlab.com/TG1999/fetchcode",
    ]
    with pytest.raises(Exception) as e_info:
        for url in invalid_urls:
            fetch_via_git(url)
            assert "Not a Git based scheme." == e_info
