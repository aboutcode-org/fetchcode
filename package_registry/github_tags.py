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


def build_url(url):
    """
    Return a URL to access the list of tags using the GitHub API 
    """
    base_url='https://api.github.com/repos'
    url_parts = urlparse(url)
    path_parts = url_parts.path.split('/')
    namespace = path_parts[1]
    name = path_parts[2]
    return '{}/{}/{}/tags'.format(base_url, namespace, name)


def get_tags(url):
    """
    Return a list of git tags  given the `url` to a Github repository
    """
    
    url_parts = urlparse(url)
    
    if not(url_parts.netloc == 'github.com'):
        raise Exception('Not a GitHub URL')
    
    else:
        final_url = build_url(url)
        resp = requests.get(final_url)
        tags = []
        for res in resp.json():
            if 'name' in res:
                tags.append(res['name'])
        return tags
