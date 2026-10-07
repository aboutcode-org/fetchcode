# fetchcode is a free software tool from nexB Inc. and others.
# Visit https://github.com/aboutcode-org/fetchcode for support and download.

# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and http://aboutcode.org

# This software is licensed under the Apache License version 2.0.

# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at:
# http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import pytest
from packageurl import PackageURL

from fetchcode import package_util


@pytest.mark.parametrize("source_tag", ["v1.2.3", "release-1_2_3", None])
def test_cocoapods_source_tag_preserves_package_version(monkeypatch, source_tag):
    monkeypatch.setattr(
        package_util.utils,
        "get_response",
        lambda url: {
            "source": {"git": "https://github.com/example/Example.git", "tag": source_tag},
        },
    )
    purl = PackageURL(type="cocoapods", name="Example", version="1.2.3")
    package = package_util.construct_cocoapods_package(
        purl, "Example", "a/b/c", "https://cocoapods.org/pods/Example", None, None, "1.2.3"
    )
    assert package.version == "1.2.3"
    assert (
        package.download_url
        == f"https://github.com/example/Example/archive/refs/tags/{source_tag or '1.2.3'}.tar.gz"
    )
