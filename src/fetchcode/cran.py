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

from fetchcode.utils import _http_exists


class Cran:
    def get_download_url(purl: str):
        """
        Resolve a CRAN PURL to a verified, downloadable source tarball URL.
        Tries current contrib first, then Archive.
        """
        p = PackageURL.from_string(purl)
        if not p.name or not p.version:
            return None

        current_url = f"https://cran.r-project.org/src/contrib/{p.name}_{p.version}.tar.gz"
        if _http_exists(current_url):
            return current_url

        archive_url = (
            f"https://cran.r-project.org/src/contrib/Archive/{p.name}/{p.name}_{p.version}.tar.gz"
        )
        if _http_exists(archive_url):
            return archive_url

        return None
