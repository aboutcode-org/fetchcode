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

import urllib.parse

from packageurl import PackageURL

from fetchcode import fetch_json_response
from fetchcode.utils import _http_exists


class CPAN:
    purl_pattern = "pkg:cpan/.*"
    base_url = "https://cpan.metacpan.org/"

    def get_download_url(purl: str):
        """
        Resolve a CPAN PURL to a verified, downloadable archive URL.
        Strategy: MetaCPAN API -> verified URL; fallback to author-based path if available.
        """
        p = PackageURL.from_string(purl)
        if not p.name or not p.version:
            return None

        try:
            parsed_name = urllib.parse.quote(p.name)
            parsed_version = urllib.parse.quote(p.version)
            api = f"https://fastapi.metacpan.org/v1/release/{parsed_name}/{parsed_version}"
            data = fetch_json_response(url=api)
            url = data.get("download_url") or data.get("archive")
            if url and _http_exists(url):
                return url
        except Exception:
            pass

        author = p.namespace
        if author:
            auth = author.upper()
            a = auth[0]
            ab = auth[:2] if len(auth) >= 2 else auth
            for ext in (".tar.gz", ".zip"):
                url = f"https://cpan.metacpan.org/authors/id/{a}/{ab}/{auth}/{p.name}-{p.version}{ext}"
                if _http_exists(url):
                    return url
