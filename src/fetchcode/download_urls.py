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

from packageurl.contrib.route import NoRouteAvailable
from packageurl.contrib.route import Router

from fetchcode.composer import Composer
from fetchcode.cpan import CPAN
from fetchcode.cran import CRAN
from fetchcode.huggingface import Huggingface
from fetchcode.pypi import Pypi

package_registry = [Pypi, CRAN, CPAN, Huggingface, Composer]

router = Router()

for pkg_class in package_registry:
    router.append(pattern=pkg_class.purl_pattern, endpoint=pkg_class.get_download_url)


def download_url(purl):
    """
    Return package metadata for a URL or PURL.
    Return None if there is no URL, or the URL or PURL is not supported.
    """
    if purl:
        try:
            return router.process(purl)
        except NoRouteAvailable:
            return
