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

from urllib.parse import urljoin

from packageurl import PackageURL

from fetchcode import fetch_json_response


class Pypi:
    """
    This class handles Pypi PURLs.
    """

    purl_pattern = "pkg:pypi/.*"
    base_url = "https://pypi.org/pypi/"

    @classmethod
    def get_download_url(cls, purl):
        """
        Return the download URL for a Pypi PURL.
        """
        purl = PackageURL.from_string(purl)

        name = purl.name
        version = purl.version

        if not name or not version:
            raise ValueError("Pypi PURL must specify a name and version")

        url = urljoin(cls.base_url, f"{name}/{version}/json")
        data = fetch_json_response(url)

        download_urls = data.get("urls", [{}])

        if not download_urls:
            raise ValueError(f"No download URLs found for {name} version {version}")

        download_url = next((url["url"] for url in download_urls if url.get("url")), None)

        if not download_url:
            raise ValueError(f"No download URL found for {name} version {version}")

        return download_url
