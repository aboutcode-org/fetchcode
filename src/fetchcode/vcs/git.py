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
import tempfile
from urllib.parse import urlparse

from fetchcode.vcs.pip._internal.vcs.git import Git
from fetchcode.vcs.pip._internal.utils import misc
from fetchcode.vcs.pip._internal.vcs import vcs
from fetchcode.vcs import VCSResponse


def fetch_via_git(url):
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    domain = parsed_url.netloc
    temp = tempfile.mkdtemp()
    os.rmdir(temp)
    if scheme not in Git.schemes:
        raise Exception("Not a Git based scheme.")

    backend = vcs.get_backend(name="git")
    backend.obtain(dest=temp, url=misc.hide_url(url))

    return VCSResponse(dest_dir=temp, vcs_type="git", domain=domain)
