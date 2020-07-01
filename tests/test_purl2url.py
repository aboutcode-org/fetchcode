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

from fetchcode.purl2url import purl2url


def test_convert_with_purls_string():
    purls_url = {
        "pkg:github/tg1999/fetchcode": "https://github.com/tg1999/fetchcode",
        "pkg:github/tg1999/fetchcode@master": "https://github.com/tg1999/fetchcode/tree/master",
        "pkg:github/tg1999/fetchcode@master#tests": "https://github.com/tg1999/fetchcode/tree/master/tests",
        "pkg:github": None,
        "pkg:github/tg1999": None,
        "pkg:cargo/clap@2.3.3": "https://crates.io/api/v1/crates/clap/2.3.3/download",
        "pkg:cargo/rand@0.7.2": "https://crates.io/api/v1/crates/rand/0.7.2/download",
        "pkg:cargo/structopt@0.3.11": "https://crates.io/api/v1/crates/structopt/0.3.11/download",
        "pkg:cargo/structopt": None,
        "pkg:cargo": None,
        "pkg:gem/jruby-launcher@1.1.2?platform=java": "https://rubygems.org/downloads/jruby-launcher-1.1.2.gem",
        "pkg:gem/ruby-advisory-db-check@0.12.4": "https://rubygems.org/downloads/ruby-advisory-db-check-0.12.4.gem",
        "pkg:gem/package-name": None,
        "pkg:gem": None,
        "pkg:bitbucket/birkenfeld/pygments-main": "https://bitbucket.org/birkenfeld/pygments-main",
        "pkg:bitbucket/birkenfeld/pygments-main@244fd47e07d1014f0aed9c": "https://bitbucket.org/birkenfeld/pygments-main/src/244fd47e07d1014f0aed9c",
        "pkg:bitbucket/birkenfeld/pygments-main@master#views": "https://bitbucket.org/birkenfeld/pygments-main/src/master/views",
        "pkg:bitbucket/birkenfeld": None,
        "pkg:bitbucket": None,
        "pkg:gitlab/tg1999/firebase@master": "https://gitlab.com/tg1999/firebase/-/tree/master",
        "pkg:gitlab/tg1999/firebase@1a122122#views": "https://gitlab.com/tg1999/firebase/-/tree/1a122122/views",
        "pkg:gitlab/tg1999/firebase": "https://gitlab.com/tg1999/firebase",
        "pkg:gitlab/tg1999": None,
        "pkg:gitlab": None,
    }

    for purl, url in purls_url.items():
        assert url == purl2url(purl)
