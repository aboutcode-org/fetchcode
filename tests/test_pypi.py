import unittest
from unittest.mock import patch
from fetchcode.pypi import Pypi

class TestGetDownloadURL(unittest.TestCase):

    @patch("fetchcode.pypi.fetch_json_response")
    def test_valid_purl_returns_download_url(self, mock_fetch_json_response):
        mock_response = {
            "urls": [
                {
                    "url": "https://files.pythonhosted.org/packages/source/r/requests/requests-2.31.0.tar.gz"
                }
            ]
        }
        mock_fetch_json_response.return_value = mock_response

        purl = "pkg:pypi/requests@2.31.0"
        result = Pypi.get_download_url(purl)
        self.assertEqual(
            result,
            "https://files.pythonhosted.org/packages/source/r/requests/requests-2.31.0.tar.gz"
        )

    @patch("fetchcode.pypi.fetch_json_response")
    def test_missing_version_raises_value_error(self, mock_fetch_json_response):
        purl = "pkg:pypi/requests"
        with self.assertRaises(ValueError) as context:
            Pypi.get_download_url(purl)
        self.assertIn("Pypi PURL must specify a name and version", str(context.exception))

    @patch("fetchcode.pypi.fetch_json_response")
    def test_missing_name_raises_value_error(self, mock_fetch_json_response):
        purl = "pkg:pypi/@2.31.0"
        with self.assertRaises(ValueError) as context:
            Pypi.get_download_url(purl)
        self.assertIn("purl is missing the required name component", str(context.exception))

    @patch("fetchcode.pypi.fetch_json_response")
    def test_missing_urls_field_raises_value_error(self, mock_fetch_json_response):
        mock_fetch_json_response.return_value = {}
        purl = "pkg:pypi/requests@2.31.0"
        with self.assertRaises(ValueError) as context:
            Pypi.get_download_url(purl)
        self.assertIn("No download URL found", str(context.exception))

    @patch("fetchcode.pypi.fetch_json_response")
    def test_empty_urls_list_raises_value_error(self, mock_fetch_json_response):
        mock_fetch_json_response.return_value = {"urls": []}
        purl = "pkg:pypi/requests@2.31.0"
        with self.assertRaises(ValueError) as context:
            Pypi.get_download_url(purl)
        self.assertIn("No download URLs found", str(context.exception))

    @patch("fetchcode.pypi.fetch_json_response")
    def test_first_url_object_missing_url_key(self, mock_fetch_json_response):
        mock_fetch_json_response.return_value = {
            "urls": [{}]
        }
        purl = "pkg:pypi/requests@2.31.0"
        with self.assertRaises(ValueError) as context:
            Pypi.get_download_url(purl)
        self.assertIn("No download URL found", str(context.exception))

    @patch("fetchcode.pypi.fetch_json_response")
    def test_url_fallback_when_multiple_urls_provided(self, mock_fetch_json_response):
        mock_fetch_json_response.return_value = {
            "urls": [
                {},
                {"url": "https://example.com/fallback-url.tar.gz"}
            ]
        }

        purl = "pkg:pypi/requests@2.31.0"
        download_url = Pypi.get_download_url(purl)
        self.assertEqual(download_url, "https://example.com/fallback-url.tar.gz")

    def test_malformed_purl_raises_exception(self):
        with self.assertRaises(ValueError):
            Pypi.get_download_url("this-is-not-a-valid-purl")
