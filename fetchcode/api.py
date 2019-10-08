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

import tempfile 

import requests


class Response:
    """
    Represent the response from fetching a URL with:
- `location`: the absolute location of the files that was fetched
- `content_type`: content type of the file
- `size`: size of the retrieved content in bytes
- `url`: fetched URL
    """
    def __init__(self, location, content_type, size, url):
        self.location = location
        self.content_type = content_type
        self.size = size
        self.url = url
 

def fetch(url):
    """
    Return a `Response` object built from fetching the content at the `url` URL string.
    """
    r = requests.get(url)

    temp = tempfile.NamedTemporaryFile(delete=False)
    filename = temp.name

    with open(filename,'wb') as f:
        f.write(r.content)

    resp = Response(location=filename,
                    content_type=r.headers['content-type'],
                    size=int(r.headers['content-length']),
                    url=url)

    return resp
