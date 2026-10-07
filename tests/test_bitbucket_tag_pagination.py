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
    "version,expected,page_count",
    [(None, ["1.0", "2.0"], 2), ("2.0", ["2.0"], 2), ("1.0", ["1.0"], 1)],
)
def test_bitbucket_tag_pagination(monkeypatch, version, expected, page_count):
    base = "https://api.bitbucket.org/2.0/repositories/example/project"
    first = base + "/refs/tags"
    second = first + "?page=2"
    responses = {
        base: {"links": {"tags": {"href": first}}},
        first: {"values": [{"name": "1.0"}], "next": second},
        second: {"values": [{"name": "2.0"}]},
    }
    calls = []

    def response(url):
        calls.append(url)
        return responses[url]

    monkeypatch.setattr(package, "get_response", response)
    purl = "pkg:bitbucket/example/project" + ("@" + version if version else "")
    result = list(package.get_bitbucket_data_from_purl(purl))
    assert [item.version for item in result] == expected
    assert len(calls) == 1 + page_count
