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


class Composer:

    purl_pattern = "pkg:composer/.*"
    base_url = "https://repo.packagist.org"

    @classmethod
    def get_download_url(cls, purl):
        """
        Return the download URL for a Composer PURL.
        """
        purl = PackageURL.from_string(purl)

        if not purl.name or not purl.version:
            raise ValueError("Composer PURL must specify a name and version")

        name = f"{purl.namespace}/{purl.name}" if purl.namespace else purl.name

        url = f"{cls.base_url}/p2/{name}.json"
        data = fetch_json_response(url)

        if "packages" not in data:
            return

        if name not in data["packages"]:
            return

        for package in data["packages"][name]:
            version = purl.version
            if any(
                package.get(field) in (version, f"v{version}")
                for field in ("version", "version_normalized")
            ):
                return package["dist"].get("url")
