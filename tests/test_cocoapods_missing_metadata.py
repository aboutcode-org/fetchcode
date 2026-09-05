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

from fetchcode import package


def test_cocoapods_with_no_versions(monkeypatch):
    monkeypatch.setattr(package, "get_cocoapod_tags", lambda *args: None)
    assert list(package.get_cocoapods_data_from_purl("pkg:cocoapods/Example")) == []


def test_cocoapods_without_homepage(monkeypatch):
    monkeypatch.setattr(package, "get_cocoapod_tags", lambda *args: ["1.0"])
    monkeypatch.setattr(package, "get_response", lambda url: {})
    sentinel = object()
    monkeypatch.setattr(package, "construct_cocoapods_package", lambda *args: sentinel)
    assert list(package.get_cocoapods_data_from_purl("pkg:cocoapods/Example")) == [sentinel]
