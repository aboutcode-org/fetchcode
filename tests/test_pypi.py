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

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from fetchcode.pypi import Pypi

DATA_DIR = Path(__file__).parent / "data" / "pypi"


def load_fixture(filename):
    with open(DATA_DIR / filename) as f:
        return json.load(f)


ASGIREF_VERSION_RESPONSE = load_fixture("asgiref-3.11.0.json")
ASGIREF_LATEST_RESPONSE = load_fixture("asgiref.json")


def mock_fetch_json_response(url):
    """Return appropriate fixture based on request URL."""
    if url == "https://pypi.org/pypi/asgiref/3.11.0/json":
        return ASGIREF_VERSION_RESPONSE
    elif url == "https://pypi.org/pypi/asgiref/json":
        return ASGIREF_LATEST_RESPONSE
    raise ValueError(f"Unexpected URL: {url}")


@patch("fetchcode.pypi.fetch_json_response", side_effect=mock_fetch_json_response)
class TestPypi(unittest.TestCase):
    def test_get_download_url_with_version(self, mock_fetch):
        purl = "pkg:pypi/asgiref@3.11.0"
        result = Pypi.get_download_url(purl)
        self.assertEqual(
            result,
            "https://files.pythonhosted.org/packages/76/b9/4db2509eabd14b4a8c71d1b24c8d5734c52b8560a7b1e1a8b56c8d25568b/asgiref-3.11.0.tar.gz",
        )
        mock_fetch.assert_called_once_with("https://pypi.org/pypi/asgiref/3.11.0/json")

    def test_get_download_url_without_version_fetches_latest(self, mock_fetch):
        purl = "pkg:pypi/asgiref"
        result = Pypi.get_download_url(purl)
        self.assertEqual(
            result,
            "https://files.pythonhosted.org/packages/76/b9/4db2509eabd14b4a8c71d1b24c8d5734c52b8560a7b1e1a8b56c8d25568b/asgiref-3.11.0.tar.gz",
        )
        mock_fetch.assert_called_once_with("https://pypi.org/pypi/asgiref/json")

    def test_get_download_url_prefers_sdist_by_default(self, mock_fetch):
        purl = "pkg:pypi/asgiref@3.11.0"
        result = Pypi.get_download_url(purl)
        self.assertIn(".tar.gz", result)

    def test_get_download_url_with_preferred_type_wheel(self, mock_fetch):
        purl = "pkg:pypi/asgiref@3.11.0"
        result = Pypi.get_download_url(purl, preferred_type="bdist_wheel")
        self.assertEqual(
            result,
            "https://files.pythonhosted.org/packages/91/be/317c2c55b8bbec407257d45f5c8d1b6867abc76d12043f2d3d58c538a4ea/asgiref-3.11.0-py3-none-any.whl",
        )

    def test_get_download_url_falls_back_to_first_when_preferred_not_found(self, mock_fetch):
        purl = "pkg:pypi/asgiref@3.11.0"
        result = Pypi.get_download_url(purl, preferred_type="nonexistent_type")
        # Falls back to first URL in the list (wheel)
        self.assertEqual(
            result,
            "https://files.pythonhosted.org/packages/91/be/317c2c55b8bbec407257d45f5c8d1b6867abc76d12043f2d3d58c538a4ea/asgiref-3.11.0-py3-none-any.whl",
        )

    def test_get_all_download_urls(self, mock_fetch):
        purl = "pkg:pypi/asgiref@3.11.0"
        result = Pypi.get_all_download_urls(purl)
        self.assertEqual(
            result,
            [
                "https://files.pythonhosted.org/packages/91/be/317c2c55b8bbec407257d45f5c8d1b6867abc76d12043f2d3d58c538a4ea/asgiref-3.11.0-py3-none-any.whl",
                "https://files.pythonhosted.org/packages/76/b9/4db2509eabd14b4a8c71d1b24c8d5734c52b8560a7b1e1a8b56c8d25568b/asgiref-3.11.0.tar.gz",
            ],
        )

    def test_get_all_download_urls_without_version(self, mock_fetch):
        purl = "pkg:pypi/asgiref"
        result = Pypi.get_all_download_urls(purl)
        self.assertEqual(
            result,
            [
                "https://files.pythonhosted.org/packages/91/be/317c2c55b8bbec407257d45f5c8d1b6867abc76d12043f2d3d58c538a4ea/asgiref-3.11.0-py3-none-any.whl",
                "https://files.pythonhosted.org/packages/76/b9/4db2509eabd14b4a8c71d1b24c8d5734c52b8560a7b1e1a8b56c8d25568b/asgiref-3.11.0.tar.gz",
            ],
        )

    def test_get_urls_info(self, mock_fetch):
        purl = "pkg:pypi/asgiref@3.11.0"
        result = Pypi.get_urls_info(purl)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["packagetype"], "bdist_wheel")
        self.assertEqual(result[1]["packagetype"], "sdist")

    def test_get_package_data(self, mock_fetch):
        purl = "pkg:pypi/asgiref@3.11.0"
        result = Pypi.get_package_data(purl)
        self.assertEqual(result["info"]["name"], "asgiref")
        self.assertEqual(result["info"]["version"], "3.11.0")


class TestPypiEdgeCases(unittest.TestCase):
    """Tests that require custom mock responses."""

    @patch("fetchcode.pypi.fetch_json_response")
    def test_get_download_url_returns_none_when_no_urls(self, mock_fetch):
        mock_fetch.return_value = {"info": {}, "urls": []}
        purl = "pkg:pypi/asgiref@3.11.0"
        result = Pypi.get_download_url(purl)
        self.assertIsNone(result)

    @patch("fetchcode.pypi.fetch_json_response")
    def test_get_download_url_returns_none_when_missing_urls_field(self, mock_fetch):
        mock_fetch.return_value = {"info": {}}
        purl = "pkg:pypi/asgiref@3.11.0"
        result = Pypi.get_download_url(purl)
        self.assertIsNone(result)

    @patch("fetchcode.pypi.fetch_json_response")
    def test_get_all_download_urls_returns_empty_list_when_no_urls(self, mock_fetch):
        mock_fetch.return_value = {"info": {}, "urls": []}
        purl = "pkg:pypi/asgiref@3.11.0"
        result = Pypi.get_all_download_urls(purl)
        self.assertEqual(result, [])

    @patch("fetchcode.pypi.fetch_json_response")
    def test_get_all_download_urls_skips_entries_without_url_key(self, mock_fetch):
        mock_fetch.return_value = {
            "info": {},
            "urls": [
                {"packagetype": "sdist"},
                {"packagetype": "bdist_wheel", "url": "https://example.com/package.whl"},
            ],
        }
        purl = "pkg:pypi/asgiref@3.11.0"
        result = Pypi.get_all_download_urls(purl)
        self.assertEqual(result, ["https://example.com/package.whl"])

    def test_missing_name_raises_value_error(self):
        purl = "pkg:pypi/@3.11.0"
        with self.assertRaises(ValueError):
            Pypi.get_download_url(purl)

    def test_malformed_purl_raises_exception(self):
        with self.assertRaises(ValueError):
            Pypi.get_download_url("this-is-not-a-valid-purl")
