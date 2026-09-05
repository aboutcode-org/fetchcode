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

from packageurl import PackageURL

from fetchcode import package_util
from fetchcode.packagedcode_models import Package


def test_github_package_without_release_date(monkeypatch):
    monkeypatch.setattr(
        package_util.utils, "fetch_github_tags_gql", lambda purl: [("v1.2.3", None)]
    )
    purl = PackageURL("github", "example", "project")
    packages = list(package_util.get_github_packages(purl, None, None, Package(**purl.to_dict())))
    assert len(packages) == 1
    assert packages[0].version == "1.2.3"
    assert packages[0].release_date is None
