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

from fetchcode.cpan import CPAN

get_download_url = CPAN.get_download_url


@pytest.fixture
def valid_purl():
    return "pkg:cpan/EXAMPLE/Some-Module@1.2.3"


def test_success_from_metacpan_api(valid_purl):
    expected_url = "https://cpan.metacpan.org/authors/id/E/EX/EXAMPLE/Some-Module-1.2.3.tar.gz"

    with patch("fetchcode.cpan.fetch_json_response") as mock_fetch, patch(
        "fetchcode.cpan._http_exists"
    ) as mock_exists:
        mock_fetch.return_value = {"download_url": expected_url}
        mock_exists.return_value = True
        result = get_download_url(valid_purl)
        assert result == expected_url
        mock_fetch.assert_called_once()
        assert mock_exists.call_count == 2


def test_fallback_to_author_path(valid_purl):
    expected_url = "https://cpan.metacpan.org/authors/id/E/EX/EXAMPLE/Some-Module-1.2.3.tar.gz"

    with patch("fetchcode.cpan.fetch_json_response", side_effect=Exception("API error")), patch(
        "fetchcode.cpan._http_exists"
    ) as mock_exists:

        mock_exists.side_effect = lambda url: url.endswith(".tar.gz")

        result = get_download_url(valid_purl)
        assert result == expected_url
        assert mock_exists.call_count >= 1


def test_author_zip_fallback(valid_purl):
    tar_url = "https://cpan.metacpan.org/authors/id/E/EX/EXAMPLE/Some-Module-1.2.3.tar.gz"
    zip_url = "https://cpan.metacpan.org/authors/id/E/EX/EXAMPLE/Some-Module-1.2.3.zip"

    with patch("fetchcode.cpan.fetch_json_response", return_value={}), patch(
        "fetchcode.cpan._http_exists"
    ) as mock_exists:

        mock_exists.side_effect = lambda url: url == zip_url

        result = get_download_url(valid_purl)
        assert result == zip_url
        assert mock_exists.call_count == 3
        assert tar_url in [call[0][0] for call in mock_exists.call_args_list]


def test_neither_api_nor_fallback_works(valid_purl):
    with patch("fetchcode.cpan.fetch_json_response", return_value={}), patch(
        "fetchcode.cpan._http_exists", return_value=False
    ) as mock_exists:

        result = get_download_url(valid_purl)
        assert result is None
        assert mock_exists.call_count == 3


def test_missing_name_or_version():
    assert get_download_url("pkg:cpan/EXAMPLE/Some-Module") is None
