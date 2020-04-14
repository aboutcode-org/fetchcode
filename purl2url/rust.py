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

from urllib.parse import urlparse


def get_rust_url(purl):
    """
    Return a downloadable normalized URL for a given rust based `purl`
    """
    url_parts = urlparse(purl)
    scheme = url_parts.scheme
    if scheme != 'pkg':
        raise Exception('Not a valid PURL, `scheme` of URL should be `pkg` to be it a PURL for more info refer https://github.com/package-url/purl-spec/blob/master/README.rst') 

    path = url_parts.path
    part_paths = path.split('@')
    version = part_paths[1]

    part_paths = part_paths[0].split('/')
    if part_paths[0] != 'cargo':
        raise Exception('Not a valid cargo PURL, `type` of PURL should be `cargo` for more info refer https://github.com/package-url/purl-spec/blob/master/README.rst')
    
    name = part_paths[1]
    return 'https://crates.io/api/v1/crates/{}/{}/download'.format(name,version)
