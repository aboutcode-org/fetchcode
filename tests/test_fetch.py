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

from unittest import mock

import pytest

from fetchcode import fetch
from fetchcode import resolve_purl
from fetchcode import resolve_url_from_purl


@mock.patch("fetchcode.requests.get")
def test_fetch_http_with_tempfile(mock_get):
    mock_get.return_value.headers = {
        "content-type": "image/png",
        "content-length": "1000999",
    }

    with mock.patch("fetchcode.open", mock.mock_open()) as mocked_file:
        url = "https://raw.githubusercontent.com/TG1999/converge/master/assets/Group%2022.png"
        response = fetch(url=url)
        assert response is not None
        assert 1000999 == response.size
        assert url == response.url
        assert "image/png" == response.content_type


@mock.patch("fetchcode.FTP")
def test_fetch_with_wrong_url(mock_get):
    with pytest.raises(Exception) as e_info:
        url = "ftp://speedtest/1KB.zip"
        response = fetch(url=url)
        assert "Not a valid URL" == e_info


@mock.patch("fetchcode.FTP", autospec=True)
def test_fetch_ftp_with_tempfile(mock_ftp_constructor):
    mock_ftp = mock_ftp_constructor.return_value
    mock_ftp_constructor.return_value.size.return_value = 1024
    with mock.patch("fetchcode.open", mock.mock_open()) as mocked_file:
        response = fetch("ftp://speedtest.tele2.net/1KB.zip")
        assert 1024 == response.size
        mock_ftp_constructor.assert_called_with("speedtest.tele2.net")
        assert mock_ftp.login.called
        mock_ftp.cwd.assert_called_with("/")
        assert mock_ftp.retrbinary.called


def test_fetch_with_scheme_not_present():
    with pytest.raises(Exception) as e_info:
        url = "abc://speedtest/1KB.zip"
        response = fetch(url=url)
        assert "Not a supported/known scheme." == e_info


@mock.patch("fetchcode._http_exists")
@mock.patch("fetchcode.fetch_http")
@mock.patch("fetchcode.pypi.fetch_json_response")
def test_fetch_purl_with_fetchcode(mock_fetch_json_response, mock_fetch_http, mock_http_exists):
    mock_fetch_http.return_value = "mocked_purl_response"
    mock_http_exists.return_value = True
    mock_fetch_json_response.return_value = {
        "urls": [{"url": "https://example.com/sample-1.0.0.zip"}]
    }

    response = fetch("pkg:pypi/sample@1.0.0")

    assert response == "mocked_purl_response"
    mock_http_exists.assert_called_once()
    mock_fetch_http.assert_called_once()


@mock.patch("fetchcode._http_exists")
@mock.patch("fetchcode.fetch_http")
def test_fetch_purl_with_purl2url(mock_fetch_http, mock_http_exists):
    mock_fetch_http.return_value = "mocked_purl_response"
    mock_http_exists.return_value = True

    response = fetch("pkg:alpm/sample@1.0.0")

    assert response == "mocked_purl_response"
    mock_http_exists.assert_called_once()
    mock_fetch_http.assert_called_once()


@mock.patch("fetchcode.pypi.fetch_json_response")
def test_fetch_invalid_purl(mock_fetch_json_response):
    mock_fetch_json_response.return_value = {}

    with pytest.raises(Exception, match="Could not resolve PURL to a valid URL."):
        fetch("pkg:pypi/invalid-package@1.0.0")


def test_fetch_unsupported_scheme():
    with pytest.raises(Exception, match="Not a supported/known scheme"):
        fetch("s3://bucket/object")


def test_resolve_url_from_purl_invalid():
    with pytest.raises(ValueError, match="Could not resolve PURL to a valid URL."):
        fetch("pkg:invalid/invalid-package@1.0.0")


@mock.patch("fetchcode._http_exists")
def test_resolve_url_from_purl_using_purl2url(mock_http_exists):
    mock_http_exists.return_value = True

    url, _ = resolve_url_from_purl("pkg:swift/github.com/Alamofire/Alamofire@5.4.3")
    assert url == "https://github.com/Alamofire/Alamofire/archive/5.4.3.zip"
    mock_http_exists.assert_called_once_with(
        "https://github.com/Alamofire/Alamofire/archive/5.4.3.zip"
    )


@mock.patch("fetchcode._http_exists")
@mock.patch("fetchcode.pypi.fetch_json_response")
def test_resolve_url_from_purl_using_fetchcode(mock_fetch_json_response, mock_http_exists):
    mock_http_exists.return_value = True
    mock_fetch_json_response.return_value = {
        "urls": [{"url": "https://example.com/sample-1.0.0.zip"}]
    }

    url, _ = resolve_url_from_purl("pkg:pypi/example@1.0.0")
    assert url == "https://example.com/sample-1.0.0.zip"
    mock_http_exists.assert_called_once_with("https://example.com/sample-1.0.0.zip")


def test_resolve_purl_invalid():
    assert resolve_purl("pkg:invalid/invalid-package@1.0.0") is None


def test_resolve_purl_using_purl2url():
    url = resolve_purl("pkg:pub/http@0.13.3")
    assert url == "https://pub.dev/api/archives/http-0.13.3.tar.gz"


@mock.patch("fetchcode._http_exists")
def test_resolve_purl_using_purl2url_url_does_not_exists(mock_http_exists):
    mock_http_exists.return_value = False
    url = resolve_purl("pkg:pub/http@0.13.3")
    assert url is None


@mock.patch("fetchcode._http_exists")
@mock.patch("fetchcode.pypi.fetch_json_response")
def test_resolve_purl_using_fetchcode(mock_fetch_json_response, mock_http_exists):
    mock_fetch_json_response.return_value = {
        "urls": [{"url": "https://example.com/sample-1.0.0.zip"}]
    }
    mock_http_exists.return_value = True
    url = resolve_purl("pkg:pypi/example@1.0.0")
    assert url == "https://example.com/sample-1.0.0.zip"


@mock.patch("fetchcode._http_exists")
@mock.patch("fetchcode.pypi.fetch_json_response")
def test_resolve_purl_using_fetchcode_url_does_not_exists(
    mock_fetch_json_response, mock_http_exists
):
    mock_fetch_json_response.return_value = {
        "urls": [{"url": "https://example.com/sample-1.0.0.zip"}]
    }
    mock_http_exists.return_value = False
    url = resolve_purl("pkg:pypi/example@1.0.0")
    assert url is None
