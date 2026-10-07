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

from fetchcode.package_versions import composer_extract_versions


def test_composer_filters_development_versions():
    response = {
        "packages": {
            "vendor/example": [
                {"version": "dev-main"},
                {"version": "1.x-dev"},
                {"version": "v1.2.3"},
                {"version": "1.3.0-beta1"},
                {},
            ]
        }
    }
    assert [item.value for item in composer_extract_versions(response, "vendor/example")] == [
        "1.2.3",
        "1.3.0-beta1",
    ]
