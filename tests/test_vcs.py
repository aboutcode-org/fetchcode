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


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_git_http_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git+http://github.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_git_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git://github.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_git_https_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git+https://github.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_git_ssh_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git+ssh://github.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_git_file_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git+file://github.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_git_ssh_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "git+git://github.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "git"
    assert response.domain == "github.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_bzr_http_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "bzr+http://gitlab.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "bzr"
    assert response.domain == "gitlab.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_bzr_https_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "bzr+https://gitlab.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "bzr"
    assert response.domain == "gitlab.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_bzr_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "bzr://gitlab.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "bzr"
    assert response.domain == "gitlab.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_bzr_ssh_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "bzr+ssh://gitlab.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "bzr"
    assert response.domain == "gitlab.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_bzr_ftp_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "bzr+ftp://gitlab.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "bzr"
    assert response.domain == "gitlab.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_bzr_sftp_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "bzr+sftp://gitlab.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "bzr"
    assert response.domain == "gitlab.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_bzr_lp_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "bzr+lp://gitlab.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "bzr"
    assert response.domain == "gitlab.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_hg_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "hg://bitbucket.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "hg"
    assert response.domain == "bitbucket.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_hg_file_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "hg+file://bitbucket.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "hg"
    assert response.domain == "bitbucket.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_hg_http_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "hg+http://bitbucket.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "hg"
    assert response.domain == "bitbucket.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_hg_https_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "hg+https://bitbucket.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "hg"
    assert response.domain == "bitbucket.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_hg_ssh_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "hg+ssh://bitbucket.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "hg"
    assert response.domain == "bitbucket.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_hg_static_http_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "hg+static-http://bitbucket.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "hg"
    assert response.domain == "bitbucket.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_svn_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "svn://bitbucket.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "svn"
    assert response.domain == "bitbucket.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_svn_http_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "svn+http://bitbucket.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "svn"
    assert response.domain == "bitbucket.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_svn_https_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "svn+https://bitbucket.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "svn"
    assert response.domain == "bitbucket.com"


@mock.patch("fetchcode.vcs.vcs.get_backend_for_scheme")
def test_fetch_with_svn_svn_url_returns_a_response(mock_backend):
    mock_backend.return_value.obtain = obtain
    url = "svn+svn://bitbucket.com/jamesor/mongoose-versioner"
    response = fetch_via_vcs(url=url)
    assert response.vcs_type == "svn"
    assert response.domain == "bitbucket.com"


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
