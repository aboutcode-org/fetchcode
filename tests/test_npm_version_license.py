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


def test_npm_metadata_uses_release_license(monkeypatch):
    monkeypatch.setattr(
        package,
        "get_response",
        lambda url: {
            "license": "Apache-2.0",
            "versions": {
                "1.0": {"version": "1.0", "license": "MIT"},
                "2.0": {"version": "2.0", "license": "Apache-2.0"},
                "0.5": {"version": "0.5"},
            },
        },
    )
    results = list(package.get_npm_data_from_purl("pkg:npm/example"))
    assert {item.version: item.declared_license for item in results} == {
        "1.0": "MIT",
        "2.0": "Apache-2.0",
        "0.5": "Apache-2.0",
    }
