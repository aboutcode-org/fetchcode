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

from fetchcode.composer import Composer


def test_valid_composer_package_with_namespace():
    purl = "pkg:composer/laravel/framework@10.0.0"
    name = "laravel/framework"
    expected_url = f"https://repo.packagist.org/p2/{name}.json "
    download_url = "https://github.com/laravel/framework/archive/refs/tags/v10.0.0.zip"

    mock_data = {"packages": {name: [{"version": "10.0.0", "dist": {"url": download_url}}]}}

    with patch("fetchcode.composer.fetch_json_response", return_value=mock_data) as mock_fetch:
        result = Composer.get_download_url(purl)
        assert result == download_url
        mock_fetch.assert_called_once_with(expected_url)


def test_valid_composer_package_without_namespace():
    purl = "pkg:composer/some-package@1.0.0"
    name = "some-package"
    expected_url = f"https://repo.packagist.org/p2/{name}.json "
    download_url = "https://example.org/some-package-1.0.0.zip"

    mock_data = {"packages": {name: [{"version": "1.0.0", "dist": {"url": download_url}}]}}

    with patch("fetchcode.composer.fetch_json_response", return_value=mock_data) as mock_fetch:
        result = Composer.get_download_url(purl)
        assert result == download_url
        mock_fetch.assert_called_once_with(expected_url)


def test_version_not_found_returns_none():
    purl = "pkg:composer/laravel/framework@10.0.0"
    name = "laravel/framework"
    mock_data = {"packages": {name: [{"version": "9.0.0", "dist": {"url": "https://old.zip"}}]}}

    with patch("fetchcode.composer.fetch_json_response", return_value=mock_data):
        result = Composer.get_download_url(purl)
        assert result is None


def test_missing_packages_key_returns_none():
    purl = "pkg:composer/laravel/framework@10.0.0"
    with patch("fetchcode.composer.fetch_json_response", return_value={}):
        result = Composer.get_download_url(purl)
        assert result is None


def test_missing_package_name_in_data_returns_none():
    purl = "pkg:composer/laravel/framework@10.0.0"
    mock_data = {"packages": {"some/other": []}}

    with patch("fetchcode.composer.fetch_json_response", return_value=mock_data):
        result = Composer.get_download_url(purl)
        assert result is None


def test_missing_version_raises():
    purl = "pkg:composer/laravel/framework"
    with pytest.raises(ValueError, match="Composer PURL must specify a name and version"):
        Composer.get_download_url(purl)
