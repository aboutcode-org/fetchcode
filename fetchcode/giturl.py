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

from pathlib import Path
from urllib.parse import urlparse


class Response:
    """
    Represent the response from fetching a git URL with:
- `dest_dir`: destination of directory
- `url_scheme`: Scheme of URL
- `domain` : Source of git VCS (GitHub, Gitlab, Bitbucket)
- `url` : URL of repo
    """
    def __init__(self, dest_dir, url_scheme, domain, url):
        self.dest_dir = dest_dir
        self.url_scheme = url_scheme
        self.domain = domain
        self.url = url

def can_handle(source):
    """
    Take source's URL as input and then check it's scheme
    if it not exits in any of http, https or git then it's 
    not a valid VCS URL to be installed
    """
    url_parts = urlparse(source)
    if url_parts.scheme in ('https', 'git', 'git+ssh', 'ssh', 'git+https'):
        return True


def clone(source, dest, branch='master', depth=None):
    """
    Takes source, branch name, depth and destination as input
    and check if the source URL can be handled and if destination doesn't already exists
    If it doesn't exist make directory for VCS URL at that destination and clone the repo at
    that destination
    """
    if not can_handle(source):
        raise UnhandledSource('Failed to decode a Git/GitHub URL: {}'.format(source))
    
    if os.path.exists(dest):
        raise Exception('Can not clone since repository already exists')
    else:
        os.mkdir(dest)
        cmd = ['git', 'clone', source, dest, '--branch', branch]
        if depth:
            cmd.extend(['--depth', depth])
    
    os.system(' '.join(cmd))
    url_scheme = urlparse(source).scheme
    if (url_scheme == 'ssh'):
        domain = urlparse(source).netloc.split('@')[1].split(':')[0]
    else :
        domain = urlparse(source).netloc
        
    resp = Response(dest_dir=dest,
                    url_scheme=url_scheme,
                    domain=domain,
                    url=source)
    return resp


def fetch(source, branch='master', depth=None, dest=None):
    """
    Takes source, branch name, depth and destination as input
    Take out the repo's name from URL and if destination is specified
    then append repo's name with destination else append repo's name with the source directory
    And then clone the VCS URL at the destination directory
    Response-
    Returns destination directory  
    """
    url_parts = urlparse(source)
    repo_name = Path(url_parts.path).stem    
    if dest:
        dest_dir = os.path.join(dest, repo_name)
    else:
        dest_dir = os.path.join(os.getcwd(),  repo_name)
    
    return clone(source, dest_dir, branch, depth)
