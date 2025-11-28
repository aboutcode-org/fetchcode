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

from packageurl import PackageURL

from fetchcode import fetch_json_response


class Pypi:
    """Handle PyPI Package URL (PURL) resolution and download URL retrieval."""

    purl_pattern = "pkg:pypi/.*"
    base_url = "https://pypi.org/pypi"

    @classmethod
    def get_package_data(cls, purl: str) -> dict:
        """
        Fetch package data from PyPI API.

        If no version is specified in the PURL, fetches the latest version.

        Args:
            purl: A Package URL string (e.g., "pkg:pypi/requests@2.28.0")

        Returns:
            The full JSON response from PyPI API.
        """
        parsed_purl = PackageURL.from_string(purl)

        if parsed_purl.version:
            api_url = f"{cls.base_url}/{parsed_purl.name}/{parsed_purl.version}/json"
        else:
            api_url = f"{cls.base_url}/{parsed_purl.name}/json"

        return fetch_json_response(api_url)

    @classmethod
    def get_urls_info(cls, purl: str) -> list[dict]:
        """
        Collect URL info dicts from PyPI API.

        If no version is specified in the PURL, fetches the latest version.

        Returns:
            List of URL info dicts from PyPI API, or empty list if none found.
        """
        data = cls.get_package_data(purl)
        return data.get("urls", [])

    @classmethod
    def get_download_url(cls, purl: str, preferred_type: str = "sdist") -> str | None:
        """
        Get a single download URL from PyPI API.

        If no version is specified in the PURL, fetches the latest version.

        Args:
            purl: A Package URL string (e.g., "pkg:pypi/requests@2.28.0")
            preferred_type: Preferred package type (e.g., "sdist", "bdist_wheel").
                Falls back to first available if preferred type not found.

        Returns:
            The download URL, or None if not found.
        """
        urls_info = cls.get_urls_info(purl)

        if not urls_info:
            return

        for url_info in urls_info:
            if url_info.get("packagetype") == preferred_type:
                return url_info["url"]

        return urls_info[0]["url"]

    @classmethod
    def get_all_download_urls(cls, purl: str) -> list[str]:
        """
        Get all download URLs from PyPI API.

        If no version is specified in the PURL, fetches the latest version.

        Args:
            purl: A Package URL string (e.g., "pkg:pypi/requests@2.28.0")

        Returns:
            List of all available download URLs.
        """
        urls_info = cls.get_urls_info(purl)
        return [url_info["url"] for url_info in urls_info if "url" in url_info]
