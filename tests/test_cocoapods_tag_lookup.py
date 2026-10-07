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

from fetchcode.package_util import get_cocoapod_tags


def test_cocoapod_tags_skip_packages_with_same_prefix(monkeypatch):
    monkeypatch.setattr(
        "fetchcode.utils.get_text_response", lambda url: "FooBar/9.0\nFoo/1.0/2.0\n"
    )
    assert get_cocoapod_tags("https://example.com/versions", "Foo") == ["1.0", "2.0"]


def test_cocoapod_tags_return_none_when_only_prefix_matches(monkeypatch):
    monkeypatch.setattr("fetchcode.utils.get_text_response", lambda url: "FooBar/9.0\n")
    assert get_cocoapod_tags("https://example.com/versions", "Foo") is None
