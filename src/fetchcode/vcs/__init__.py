# fetchcode is a free software tool from nexB Inc. and others.
# Visit https://github.com/nexB/fetchcode for support and download.
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

import os
import shutil
import tempfile
from urllib.parse import urlparse

from fetchcode.vcs.pip._internal.vcs.bazaar import Bazaar
from fetchcode.vcs.pip._internal.vcs.git import Git
from fetchcode.vcs.pip._internal.vcs.mercurial import Mercurial
from fetchcode.vcs.pip._internal.utils import misc
from fetchcode.vcs.pip._internal.vcs.subversion import Subversion
from fetchcode.vcs.pip._internal.vcs import vcs


class VCSResponse:
    """
        Represent the response from fetching a VCS URL with:
    - `dest_dir`: destination of directory
    - `vcs_type`: VCS Type of URL (git,bzr,hg,svn)
    - `domain` : Source of git VCS (GitHub, Gitlab, Bitbucket)
    """

    def __init__(self, dest_dir, vcs_type, domain):
        self.dest_dir = dest_dir
        self.vcs_type = vcs_type
        self.domain = domain

    def delete(self):
        """
        Delete the temporary directory.
        """
        if os.path.isdir(self.dest_dir):
            shutil.rmtree(path=self.dest_dir)


def fetch_via_vcs(url):
    """
    Take `url` as input and store the content of it at location specified at `location` string
    Return a VCSResponse object
    """
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    domain = parsed_url.netloc
    dest_dir = os.path.join(tempfile.mkdtemp(), "checkout")
    if scheme not in vcs.all_schemes:
        raise Exception("Not a supported/known scheme.")

    for vcs_name, vcs_backend in vcs._registry.items():
        if scheme in vcs_backend.schemes:
            vcs_type = vcs_name

    backend = vcs.get_backend_for_scheme(scheme)
    backend.obtain(dest=dest_dir, url=misc.hide_url(url))

    return VCSResponse(dest_dir=dest_dir, vcs_type=vcs_type, domain=domain)
