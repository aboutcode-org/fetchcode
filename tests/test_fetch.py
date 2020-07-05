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

import pytest

from fetchcode import fetch


@mock.patch('fetchcode.requests.get')
def test_fetch_http_with_tempfile(mock_get):
    mock_get.return_value.headers = {
        'content-type': 'image/png',
        'content-length': '1000999',
    }

    with mock.patch('fetchcode.open', mock.mock_open()) as mocked_file:
        url = 'https://raw.githubusercontent.com/TG1999/converge/master/assets/Group%2022.png'
        response = fetch(url=url)
        assert response is not None
        assert 1000999 == response.size
        assert url == response.url
        assert 'image/png' == response.content_type


@mock.patch('fetchcode.FTP')
def test_fetch_with_wrong_url(mock_get):
    with pytest.raises(Exception) as e_info:
        url = 'ftp://speedtest/1KB.zip'
        response = fetch(url=url)
        assert 'Not a valid URL' == e_info


@mock.patch('fetchcode.FTP', autospec=True)
def test_fetch_ftp_with_tempfile(mock_ftp_constructor):
    mock_ftp = mock_ftp_constructor.return_value
    mock_ftp_constructor.return_value.size.return_value = 1024
    with mock.patch('fetchcode.open', mock.mock_open()) as mocked_file:
        response = fetch('ftp://speedtest.tele2.net/1KB.zip')
        assert 1024 == response.size
        mock_ftp_constructor.assert_called_with('speedtest.tele2.net')
        assert mock_ftp.login.called == True
        mock_ftp.cwd.assert_called_with('/')
        assert mock_ftp.retrbinary.called


def test_fetch_with_scheme_not_present():
    with pytest.raises(Exception) as e_info:
        url = 'abc://speedtest/1KB.zip'
        response = fetch(url=url)
        assert 'Not a supported/known scheme.' == e_info
