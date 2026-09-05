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

from fetchcode import package


@pytest.mark.parametrize(
    "purl,registry_name",
    [("pkg:npm/%40scope/example@1.0", "@scope/example"), ("pkg:npm/example@1.0", "example")],
)
def test_npm_metadata_preserves_scope(monkeypatch, purl, registry_name):
    urls = []

    def response(url):
        urls.append(url)
        return {"versions": {"1.0": {"version": "1.0"}}}

    monkeypatch.setattr(package, "get_response", response)
    result = list(package.get_npm_data_from_purl(purl))
    assert urls == ["http://registry.npmjs.org/" + registry_name]
    assert result[0].purl == purl
