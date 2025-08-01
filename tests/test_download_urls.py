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

from unittest.mock import patch

import pytest
from packageurl.contrib.route import NoRouteAvailable

from fetchcode.download_urls import download_url
from fetchcode.download_urls import router


def test_right_class_being_called_for_the_purls():
    purls = [
        "pkg:pypi/requests@2.31.0",
        "pkg:cpan/EXAMPLE/Some-Module@1.2.3",
        "pkg:composer/laravel/framework@10.0.0",
        "pkg:cran/dplyr@1.0.0",
    ]

    with patch("fetchcode.download_urls.Router.process") as mock_fetch:
        for purl in purls:
            assert download_url(purl) is not None, f"Failed for purl: {purl}"


def test_with_invalid_purls():
    invalid_purls = [
        "pkg:invalid/requests",
        "pkg:xyz/dplyr",
    ]
    for purl in invalid_purls:
        with pytest.raises(NoRouteAvailable):
            router.process(purl)
