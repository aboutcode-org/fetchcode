# fetchcode is a free software tool from nexB Inc. and others.
# Visit https://github.com/aboutcode-org/fetchcode for support and download.
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

from unittest.mock import patch

from fetchcode.huggingface import Huggingface


def test_returns_bin_file_url():
    purl = "pkg:huggingface/facebook/opt-350m"
    revision = "main"
    expected_url = "https://huggingface.co/facebook/opt-350m/resolve/main/pytorch_model.bin"

    mock_data = {
        "siblings": [
            {"rfilename": "config.json"},
            {"rfilename": "pytorch_model.bin"},
        ]
    }

    with patch("fetchcode.huggingface.fetch_json_response", return_value=mock_data):
        result = Huggingface.get_download_url(purl)
        assert result == expected_url


def test_no_executable_files_returns_none():
    purl = "pkg:huggingface/facebook/opt-350m"
    mock_data = {
        "siblings": [
            {"rfilename": "config.json"},
            {"rfilename": "tokenizer.json"},
        ]
    }

    with patch("fetchcode.huggingface.fetch_json_response", return_value=mock_data):
        result = Huggingface.get_download_url(purl)
        assert result is None


def test_custom_revision_in_purl():
    purl = "pkg:huggingface/facebook/opt-350m@v1.0"
    expected_url = "https://huggingface.co/facebook/opt-350m/resolve/v1.0/pytorch_model.bin"

    mock_data = {
        "siblings": [
            {"rfilename": "pytorch_model.bin"},
        ]
    }

    with patch("fetchcode.huggingface.fetch_json_response", return_value=mock_data):
        result = Huggingface.get_download_url(purl)
        assert result == expected_url
