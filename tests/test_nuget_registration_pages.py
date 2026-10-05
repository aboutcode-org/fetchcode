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

from fetchcode import package_versions


def test_nuget_fetches_external_registration_pages(monkeypatch):
    calls = []

    def response(url):
        calls.append(url)
        return {
            "items": [{"catalogEntry": {"version": "2.0", "published": "2024-01-01T00:00:00Z"}}]
        }

    monkeypatch.setattr(package_versions, "get_response", response)
    index = {
        "items": [
            {"@id": "https://example.org/inline", "items": [{"catalogEntry": {"version": "1.0"}}]},
            {"@id": "https://example.org/page2"},
            {"@id": "https://example.org/empty", "items": []},
        ]
    }
    versions = list(package_versions.nuget_extract_versions(index))
    assert [version.value for version in versions] == ["1.0", "2.0"]
    assert calls == ["https://example.org/page2"]
    assert versions[1].release_date.isoformat() == "2024-01-01T00:00:00+00:00"
