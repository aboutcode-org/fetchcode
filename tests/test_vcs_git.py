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


@pytest.mark.parametrize(
    "url, vcs_type, domain",
    [
        pytest.param("git+http://github.com/jamesor/mongoose-versioner", "git", "github.com", id="git_http"),
        pytest.param("git://github.com/jamesor/mongoose-versioner", "git", "github.com", id="git"),
        pytest.param("git+https://github.com/jamesor/mongoose-versioner", "git", "github.com", id="git_https"),
        pytest.param("git+ssh://github.com/jamesor/mongoose-versioner", "git", "github.com", id="git_ssh"),
        pytest.param("git+file://github.com/jamesor/mongoose-versioner", "git", "github.com", id="git_file"),
        pytest.param("git+git://github.com/jamesor/mongoose-versioner", "git", "github.com", id="git_git")
    ],
)
@mock.patch("fetchcode.vcs.git.vcs.get_backend")
def test_fetch_via_vcs_returns_response(mock_backend, url, vcs_type, domain):
    mock_backend.return_value.obtain = obtain
    response = fetch_via_git(url=url)
    assert response.vcs_type == vcs_type
    assert response.domain == domain

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
