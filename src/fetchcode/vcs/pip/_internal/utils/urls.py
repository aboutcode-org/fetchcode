# Copyright (c) 2008-2020 The pip developers:
# Chris Jerdonek, Jason R. Coombs
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys
from urllib.parse import urlparse

from fetchcode.vcs.pip._vendor.six.moves.urllib import request as urllib_request


def get_url_scheme(url):
    # type: (Union[str, Text]) -> Optional[Text]
    if ':' not in url:
        return None
    return url.split(':', 1)[0].lower()


def path_to_url(path):
    # type: (Union[str, Text]) -> str
    """
    Convert a path to a file: URL.  The path will be made absolute and have
    quoted path parts.
    """
    path = os.path.normpath(os.path.abspath(path))
    url = urlparse.urljoin('file:', urllib_request.pathname2url(path))
    return url


def url_to_path(url):
    # type: (str) -> str
    """
    Convert a file: URL to a path.
    """
    assert url.startswith('file:'), (
        "You can only turn file: urls into filenames (not {url!r})"
        .format(**locals()))

    _, netloc, path, _, _ = urlparse.urlsplit(url)

    if not netloc or netloc == 'localhost':
        # According to RFC 8089, same as empty authority.
        netloc = ''
    elif sys.platform == 'win32':
        # If we have a UNC path, prepend UNC share notation.
        netloc = '\\\\' + netloc
    else:
        raise ValueError(
            'non-local file URIs are not supported on this platform: {url!r}'
            .format(**locals())
        )

    path = urllib_request.url2pathname(netloc + path)
    return path
