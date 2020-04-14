# fetchcode is a free software tool from nexB Inc. and others.
# Visit https://github.com/nexB/fetchcode for support and download.
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and http://aboutcode.org
#
# This software is licensed under the Apache License version 2.0.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: 
# http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from purl2url import rust
import pytest


def test_url_2_purl_rust():
    get_url = rust.get_rust_url
    purl = 'pkg:cargo/clap@2.33.0'
    expected_url = 'https://crates.io/api/v1/crates/clap/2.33.0/download'
    url = get_url(purl=purl)
    assert expected_url == url

def test_url_2_purl_rust_special_characters():
    get_url = rust.get_rust_url
    purl = 'pkg:cargo/a3mo_lib@0.3.0'
    expected_url = 'https://crates.io/api/v1/crates/a3mo_lib/0.3.0/download'
    url = get_url(purl=purl)
    assert expected_url == url

def test_url_2_purl_rust_empty():
    with pytest.raises(Exception) as e_info:
        get_url = rust.get_rust_url
        purl = ''
        url = get_url(purl=purl)
        assert e_info == 'Not a valid PURL, `scheme` of URL should be `pkg` to be it a PURL for more info refer https://github.com/package-url/purl-spec/blob/master/README.rst'

def test_url_2_purl_rust_with_invalid_crate_purl():
    with pytest.raises(Exception) as e_info:
        get_url = rust.get_rust_url
        purl = 'pkg:github/a3mo_lib@0.3.0'
        url = get_url(purl=purl)
        assert e_info == 'Not a valid cargo PURL, `type` of PURL should be `cargo` for more info refer https://github.com/package-url/purl-spec/blob/master/README.rst'
