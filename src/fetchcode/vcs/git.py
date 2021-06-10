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
from fetchcode.vcs.pip._internal.vcs.versioncontrol import RevOptions
from fetchcode.vcs.pip._internal.utils import misc
from fetchcode.vcs.pip._internal.vcs import vcs
from fetchcode.vcs import VCSResponse


def fetch_via_git(url, location=None):
    """
    Take `url` as input and store the content of it at location specified at `location` string
    If location string is not set, a tempfile.mkdtemp() will be created to store content in.
    tempfile.mkdtemp must be cleaned by user manually.
    Return a VCSResponse object
    """
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    domain = parsed_url.netloc
    if location is None:
        location = tempfile.mkdtemp()
        os.rmdir(location)
    if scheme not in Git.schemes:
        raise Exception("Not a Git based scheme.")

    backend = vcs.get_backend(name="git")
    backend.obtain(dest=location, url=misc.hide_url(url))
    return VCSResponse(dest_dir=location, vcs_type="git", domain=domain)