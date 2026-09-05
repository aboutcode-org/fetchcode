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

from fetchcode.package_versions import get_pypi_latest_date


def test_pypi_latest_date_skips_missing_upload_times():
    assert get_pypi_latest_date([{}, {"upload_time_iso_8601": None}]) is None
    result = get_pypi_latest_date(
        [
            {},
            {"upload_time_iso_8601": "2024-01-02T00:00:00Z"},
            {},
            {"upload_time_iso_8601": "2024-01-01T00:00:00Z"},
        ]
    )
    assert result.isoformat() == "2024-01-02T00:00:00+00:00"
