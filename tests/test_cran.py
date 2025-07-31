# fetchcode is a free software tool from nexB Inc. and others.
# Visit https://github.com/aboutcode-org/fetchcode for support and download.
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

from unittest.mock import patch

import pytest

from fetchcode.cran import Cran

get_download_url = Cran.get_download_url


@pytest.fixture
def valid_purl():
    return "pkg:cran/dplyr@1.0.0"


def test_current_url_exists(valid_purl):
    current_url = "https://cran.r-project.org/src/contrib/dplyr_1.0.0.tar.gz"

    with patch("fetchcode.cran._http_exists", return_value=True) as mock_check:
        result = get_download_url(valid_purl)
        assert result == current_url
        mock_check.assert_called_once_with(current_url)


def test_fallback_to_archive(valid_purl):
    current_url = "https://cran.r-project.org/src/contrib/dplyr_1.0.0.tar.gz"
    archive_url = "https://cran.r-project.org/src/contrib/Archive/dplyr/dplyr_1.0.0.tar.gz"

    def side_effect(url):
        return url == archive_url

    with patch("fetchcode.cran._http_exists", side_effect=side_effect) as mock_check:
        result = get_download_url(valid_purl)
        assert result == archive_url
        assert mock_check.call_count == 2
        mock_check.assert_any_call(current_url)
        mock_check.assert_any_call(archive_url)


def test_neither_url_exists(valid_purl):
    with patch("fetchcode.cran._http_exists", return_value=False) as mock_check:
        result = get_download_url(valid_purl)
        assert result is None
        assert mock_check.call_count == 2


def test_missing_version_returns_none():
    result = get_download_url("pkg:cran/dplyr")
    assert result is None


def test_version_with_dash():
    purl = "pkg:cran/somepkg@1.2-3"

    with patch("fetchcode.cran._http_exists", return_value=True) as mock_check:
        result = get_download_url(purl)
        assert result == "https://cran.r-project.org/src/contrib/somepkg_1.2-3.tar.gz"
        mock_check.assert_called_once_with(
            "https://cran.r-project.org/src/contrib/somepkg_1.2-3.tar.gz"
        )


def test_name_with_dot():
    purl = "pkg:cran/foo.bar@2.0.1"

    with patch("fetchcode.cran._http_exists", return_value=True) as mock_check:
        result = get_download_url(purl)
        assert result == "https://cran.r-project.org/src/contrib/foo.bar_2.0.1.tar.gz"
        mock_check.assert_called_once_with(
            "https://cran.r-project.org/src/contrib/foo.bar_2.0.1.tar.gz"
        )
