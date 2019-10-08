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

import os
from unittest import mock

from fetchcode import api

@mock.patch('fetchcode.api.requests.get')
def test_fetch(mock_get):

    with mock.patch('fetchcode.api.open', mock.mock_open()) as mocked_file:
        url = 'https://raw.githubusercontent.com/lk-geimfari/unittest/master/logo.png'
        response = api.fetch(url=url)
        assert response is not None
        assert hasattr(response,'size')
        assert hasattr(response,'location')
        assert hasattr(response,'url')
        assert hasattr(response,'content_type') 
