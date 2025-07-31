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

from packageurl import PackageURL

from fetchcode import fetch_json_response


class Huggingface:
    """
    This class handles huggingface PURLs.
    """

    purl_pattern = "pkg:huggingface/.*"

    @classmethod
    def get_download_url(cls, purl: str):
        """
        Return the download URL for a Hugging Face PURL.
        """
        p = PackageURL.from_string(purl)
        if not p.name:
            return None

        revision = p.version or "main"
        model_id = p.name
        q = p.qualifiers or {}

        api_url = f"https://huggingface.co/api/models/{model_id}?revision={revision}"
        data = fetch_json_response(api_url)
        siblings = data.get("siblings", [])

        ALLOWED_EXECUTABLE_EXTS = (".bin",)

        for sib in siblings:
            file_name = sib.get("rfilename")
            if not file_name.endswith(ALLOWED_EXECUTABLE_EXTS):
                continue
            url = f"https://huggingface.co/{model_id}/resolve/{revision}/{file_name}"
            return url
