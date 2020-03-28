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

from unittest import mock

from fetchcode import giturl


@mock.patch('os.system')
def test_fetch_with_https_url_returns_a_response(mock_os):
    url = 'https://github.com/TG1999/fetchcode.git'
    with mock.patch('os.mkdir') as mocked_file:
        response = giturl.fetch(source=url, branch='master', depth=None, dest='/home/tg')
        assert response.url_scheme == 'https'
        assert response.domain == 'github.com'


@mock.patch('os.system')
def test_fetch_with_git_url_returns_a_response(mock_os):
    url = 'git://github.com/jamesor/mongoose-versioner'
    with mock.patch('os.mkdir') as mocked_file:
        response = giturl.fetch(source=url, branch='master', depth=None, dest='/home/tg')
        assert response.url_scheme == 'git'
        assert response.domain == 'github.com'


@mock.patch('os.system')
def test_fetch_with_git_ssh_url_returns_a_response(mock_os):
    url = 'git+ssh://github.com/bcoe/thumbd.git'
    with mock.patch('os.mkdir') as mocked_file:
        response = giturl.fetch(source=url, branch='master', depth=None, dest='/home/tg')
        assert response.url_scheme == 'git+ssh'
        assert response.domain == 'github.com'


@mock.patch('os.system')
def test_fetch_with_git_https_url_returns_a_response(mock_os):
    url = 'git+https://github.com/Empeeric/i18n-node'
    with mock.patch('os.mkdir') as mocked_file:
        response = giturl.fetch(source=url, branch='master', depth=None, dest='/home/tg')
        assert response.url_scheme == 'git+https'
        assert response.domain == 'github.com'


@mock.patch('os.system')
def test_fetch_with_ssh_url_returns_a_response(mock_os):
    url = 'ssh://git@github.com:EastCloud/node-websockets.git'
    with mock.patch('os.mkdir') as mocked_file:
        response = giturl.fetch(source=url, branch='master', depth=None, dest='/home/tg')
        assert response.url_scheme == 'ssh'
        assert response.domain == 'github.com'
