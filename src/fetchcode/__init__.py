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

import os
import tempfile
from ftplib import FTP
from mimetypes import MimeTypes
from urllib.parse import urlparse

import requests
from packageurl.contrib import purl2url

from fetchcode.utils import _http_exists


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
    Return a `Response` object built from fetching the content at a HTTP/HTTPS based
    `url` URL string saving the content in a file at `location`
    """
    r = requests.get(url)

    with open(location, "wb") as f:
        f.write(r.content)

    content_type = r.headers.get("content-type")
    size = r.headers.get("content-length")
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
    file = "RETR {}".format(file)
    with open(location, "wb") as f:
        ftp.retrbinary(file, f.write)
    ftp.close()

    resp = Response(location=location, content_type=content_type, size=size, url=url)
    return resp


def resolve_purl(purl):
    """
    Resolve a Package URL (PURL) to a download URL.

    This function attempts to resolve the PURL using both the purl2url library and
    the fetchcode.download_urls module. It returns the first valid download URL found.
    """
    from fetchcode.download_urls import download_url as get_download_url_from_fetchcode

    for resolver in (purl2url.get_download_url, get_download_url_from_fetchcode):
        url = resolver(purl)
        if url and _http_exists(url):
            return url


def fetch(url):
    """
    Return a `Response` object built from fetching the content at the `url` URL string and
    store content at a temporary file.
    """
    url_parts = urlparse(url)
    scheme = url_parts.scheme

    if scheme == "pkg":
        url = resolve_purl(url)
        url_parts = urlparse(url)
        scheme = url_parts.scheme

    temp = tempfile.NamedTemporaryFile(delete=False)
    location = temp.name

    fetchers = {"ftp": fetch_ftp, "http": fetch_http, "https": fetch_http}

    if scheme in fetchers:
        return fetchers.get(scheme)(url, location)

    raise Exception("Not a supported/known scheme.")


def fetch_json_response(url):
    """
    Fetch a JSON response from the given URL and return the parsed JSON data.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}: {response.status_code} {response.reason}")

    try:
        return response.json()
    except ValueError as e:
        raise Exception(f"Failed to parse JSON from {url}: {str(e)}")
