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

from fetchcode.vcs import fetch_via_vcs
from fetchcode.vcs.pip._internal.vcs import vcs


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
        pytest.param("git+git://github.com/jamesor/mongoose-versioner", "git", "github.com", id="git_git"),
        pytest.param("bzr+http://gitlab.com/jamesor/mongoose-versioner", "bzr", "gitlab.com", id="bzr_http"),
        pytest.param("bzr+https://gitlab.com/jamesor/mongoose-versioner", "bzr", "gitlab.com", id="bzr_https"),
        pytest.param("bzr://gitlab.com/jamesor/mongoose-versioner", "bzr", "gitlab.com", id="bzr"),
        pytest.param("bzr+ssh://gitlab.com/jamesor/mongoose-versioner", "bzr", "gitlab.com", id="bzr_ssh"),
        pytest.param("bzr+ftp://gitlab.com/jamesor/mongoose-versioner", "bzr", "gitlab.com", id="bzr_ftp"),
        pytest.param("bzr+sftp://gitlab.com/jamesor/mongoose-versioner", "bzr", "gitlab.com", id="bzr_sftp"),
        pytest.param("bzr+lp://gitlab.com/jamesor/mongoose-versioner", "bzr", "gitlab.com", id="bzr_lp"),
        pytest.param("hg://bitbucket.com/jamesor/mongoose-versioner", "hg", "bitbucket.com", id="hg"),
        pytest.param("hg+file://bitbucket.com/jamesor/mongoose-versioner", "hg", "bitbucket.com", id="hg_file"),
        pytest.param("hg+http://bitbucket.com/jamesor/mongoose-versioner", "hg", "bitbucket.com", id="hg_http"),
        pytest.param("hg+https://bitbucket.com/jamesor/mongoose-versioner", "hg", "bitbucket.com", id="hg_https"),
        pytest.param("hg+ssh://bitbucket.com/jamesor/mongoose-versioner", "hg", "bitbucket.com", id="hg_ssh"),
        pytest.param("hg+static-http://bitbucket.com/jamesor/mongoose-versioner", "hg", "bitbucket.com", id="hg_static_http"),
        pytest.param("svn://bitbucket.com/jamesor/mongoose-versioner", "svn", "bitbucket.com", id="svn"),
        pytest.param("svn+http://bitbucket.com/jamesor/mongoose-versioner", "svn", "bitbucket.com", id="svn_http"),
        pytest.param("svn+https://bitbucket.com/jamesor/mongoose-versioner", "svn", "bitbucket.com", id="svn_https"),
        pytest.param("svn+svn://bitbucket.com/jamesor/mongoose-versioner", "svn", "bitbucket.com", id="svn_svn")
    ],
)
@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_via_vcs_returns_response(mock_backend, url, vcs_type, domain):
    mock_backend.return_value.obtain = obtain
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == vcs_type
    assert response.domain == domain

def test_fetch_with_invalid_scheme():
    invalid_urls = [
        "https://github.com/TG1999/fetchcode",
        "https://bitbucket.org/TG1999/fetchcode",
        "https://gitlab.com/TG1999/fetchcode",
    ]
    with pytest.raises(Exception) as e_info:
        for url in invalid_urls:
            fetch_via_vcs(url)
            assert "Not a supported/known scheme." == e_info
