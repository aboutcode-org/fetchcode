# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See https://github.com/aboutcode-org/fetchcode for support or download.

from unittest import mock

import pytest
import requests

from fetchcode import fetch_http
from fetchcode import fetch_json_response
from fetchcode import package_versions
from fetchcode import utils


@pytest.fixture
def http_response():
    response = mock.Mock()
    response.status_code = 200
    response.json.return_value = {"name": "example"}
    response.text = "name: example"
    response.content = b"name: example"
    response.headers = {"content-type": "text/plain", "content-length": "13"}
    return response


@pytest.mark.parametrize(
    "helper, method, expected",
    [
        (utils.get_response, "get", {"name": "example"}),
        (utils.get_text_response, "get", "name: example"),
        (utils.make_head_request, "head", None),
    ],
)
def test_http_helpers_use_timeout(helper, method, expected, http_response):
    url = "https://example.com/metadata"
    headers = {"Accept": "application/json"}
    with mock.patch(f"requests.{method}", return_value=http_response) as request:
        result = helper(url, headers=headers)

    request.assert_called_once_with(url, headers=headers, timeout=30)
    assert result == (http_response if method == "head" else expected)


def test_github_graphql_uses_timeout(http_response):
    query = {"query": "query { viewer { login } }"}
    with (
        mock.patch("fetchcode.utils.get_github_token", return_value="test-token"),
        mock.patch("requests.post", return_value=http_response) as request,
    ):
        result = utils.github_response(query)

    request.assert_called_once_with(
        "https://api.github.com/graphql",
        headers={"Authorization": "bearer test-token"},
        json=query,
        timeout=30,
    )
    assert result == {"name": "example"}


def test_fetch_http_uses_timeout(tmp_path, http_response):
    url = "https://example.com/archive"
    location = tmp_path / "download"
    with mock.patch("requests.get", return_value=http_response) as request:
        result = fetch_http(url, location)

    request.assert_called_once_with(url, timeout=30)
    assert location.read_bytes() == http_response.content
    assert result.url == url
    assert result.size == 13
    assert result.content_type == "text/plain"


def test_fetch_json_response_uses_timeout(http_response):
    url = "https://example.com/metadata.json"
    with mock.patch("requests.get", return_value=http_response) as request:
        result = fetch_json_response(url)

    request.assert_called_once_with(url, timeout=30)
    assert result == {"name": "example"}


@pytest.mark.parametrize(
    "content_type, expected",
    [
        ("json", {"name": "example"}),
        ("yaml", {"name": "example"}),
        ("text", "name: example"),
        ("binary", b"name: example"),
    ],
)
def test_package_versions_response_uses_timeout(content_type, expected, http_response):
    url = "https://example.com/versions"
    with mock.patch("requests.get", return_value=http_response) as request:
        result = package_versions.get_response(url, content_type=content_type)

    request.assert_called_once_with(url, timeout=30)
    http_response.raise_for_status.assert_called_once_with()
    assert result == expected


@pytest.mark.parametrize("error_type", [requests.ConnectTimeout, requests.ReadTimeout])
@pytest.mark.parametrize(
    "helper",
    [
        utils.get_response,
        utils.get_text_response,
        fetch_json_response,
        package_versions.get_response,
    ],
)
def test_response_helpers_propagate_timeouts(helper, error_type):
    with mock.patch("requests.get", side_effect=error_type("request timed out")):
        with pytest.raises(error_type, match="request timed out"):
            helper("https://example.com/metadata")


def test_timed_out_download_does_not_overwrite_file(tmp_path):
    location = tmp_path / "download"
    location.write_bytes(b"existing content")
    with mock.patch("requests.get", side_effect=requests.ReadTimeout("request timed out")):
        with pytest.raises(requests.ReadTimeout, match="request timed out"):
            fetch_http("https://example.com/archive", location)

    assert location.read_bytes() == b"existing content"


def test_timed_out_github_graphql_request_propagates():
    with (
        mock.patch("fetchcode.utils.get_github_token", return_value="test-token"),
        mock.patch("requests.post", side_effect=requests.ReadTimeout("request timed out")),
    ):
        with pytest.raises(requests.ReadTimeout, match="request timed out"):
            utils.github_response({"query": "query { viewer { login } }"})


def test_timed_out_head_request_reports_failure():
    url = "https://example.com/archive"
    with mock.patch("requests.head", side_effect=requests.ConnectTimeout("request timed out")):
        with pytest.raises(Exception, match=f"Failed to fetch: {url}"):
            utils.make_head_request(url)
        assert utils._http_exists(url) is False
