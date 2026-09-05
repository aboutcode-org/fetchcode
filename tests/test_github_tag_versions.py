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

import datetime

import pytest
from packageurl import PackageURL

from fetchcode import package_util
from fetchcode.packagedcode_models import Package


@pytest.mark.parametrize(
    "tag,expected",
    [
        ("v1.2-dev", "1.2-dev"),
        ("v1_2_3+build_4", "1.2.3+build_4"),
        ("v1_2+build+extra", "1.2+build+extra"),
        ("vv1.2", None),
    ],
)
def test_github_tag_version_normalization(monkeypatch, tag, expected):
    monkeypatch.setattr(
        package_util.utils,
        "fetch_github_tags_gql",
        lambda purl: [(tag, datetime.datetime(2026, 1, 1))],
    )
    purl = PackageURL("github", "example", "project")
    packages = list(package_util.get_github_packages(purl, None, None, Package(**purl.to_dict())))
    if expected is None:
        assert packages == []
        return
    assert packages[0].version == expected
    assert packages[0].download_url.endswith(f"/{tag}.tar.gz")
