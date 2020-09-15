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

import requests
from urllib.parse import urlparse


def build_url(package):
    """
    Return a URL to access the list of versions using the Crates API 
    """
    base_url='https://crates.io/api/v1/crates'
    return '{}/{}'.format(base_url, package)


def get_versions(package):
    """
    Return a list of crate versions given the `package` from Crate packages
    """

    url = build_url(package)
    resp = requests.get(url)
    
    tags = []
    
    response = resp.json()
    
    versions = response.get('versions',[])
    for version in versions:
        if 'num' in version:
            tags.append(version.get('num'))
    
    return tags
