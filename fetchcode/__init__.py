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

from ftplib import FTP
from mimetypes import MimeTypes
import os
import tempfile
from urllib.parse import urlparse

import requests


class Response:
    def __init__(self, location, content_type, size, url):
        """
        Represent the response from fetching a URL with:
        - `location`: the absolute location of the files that was fetched
        - `content_type`: content type of the file
        - `size`: size of the retrieved content in bytes
        - `url`: fetched URL
        """
        self.url = url
        self.size = size
        self.content_type = content_type
        self.location = location


def fetch_http(url, location):
    """
    Return a `Response` object built from fetching the content at a HTTP/HTTPS based `url` URL string
    saving the content in a file at `location`   
    """
    r = requests.get(url)
    with open(location, 'wb') as f:
        f.write(r.content)

    content_type = r.headers.get('content-type')
    size = r.headers.get('content-length')
    size = int(size) if size else None

    resp = Response(location=location, content_type=content_type, size=size, url=url)

    return resp


def fetch_ftp(url, location):
    """
    Return a `Response` object built from fetching the content at a FTP based `url` URL string
    saving the content in a file at `location`  
    """
    url_parts = urlparse(url)

    netloc = url_parts.netloc
    path = url_parts.path
    dir, file = os.path.split(path)

    ftp = FTP(netloc)
    ftp.login()

    size = ftp.size(path)
    mime = MimeTypes()
    mime_type = mime.guess_type(file)
    if mime_type:
        content_type = mime_type[0]
    else:
        content_type = None

    ftp.cwd(dir)
    file = 'RETR {}'.format(file)
    with open(location, 'wb') as f:
        ftp.retrbinary(file, f.write)
    ftp.close()

    resp = Response(location=location, content_type=content_type, size=size, url=url)
    return resp


def fetch(url):
    """
    Return a `Response` object built from fetching the content at the `url` URL string and store content at a temporary file.
    """

    temp = tempfile.NamedTemporaryFile(delete=False)
    location = temp.name

    url_parts = urlparse(url)
    scheme = url_parts.scheme

    fetchers = {'ftp': fetch_ftp, 'http': fetch_http, 'https': fetch_http}

    if scheme in fetchers:
        return fetchers.get(scheme)(url, location)

    raise Exception('Not a supported/known scheme.')
