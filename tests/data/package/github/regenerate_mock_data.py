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

import json
import os
from pathlib import Path

from fetchcode.utils import GQL_QUERY
from fetchcode.utils import get_response
from fetchcode.utils import github_response

data_location = Path(__file__).parent


def fetch_github_mock_data(owner, name, subdir):
    """
    Fetch mock data for from GitHub.
    """
    variables = {
        "owner": owner,
        "name": name,
    }
    graphql_query = {
        "query": GQL_QUERY,
        "variables": variables,
    }
    file_count = 1
    while True:
        response = github_response(graphql_query)
        refs = response["data"]["repository"]["refs"]
        mock_data_file = data_location / \
            f"{subdir}/github_mock_data_{file_count}.json"
        with open(mock_data_file, "w") as file:
            json.dump(response, file, indent=2)

        page_info = refs["pageInfo"]
        if not page_info["hasNextPage"]:
            break

        variables["after"] = page_info["endCursor"]
        file_count += 1


GITHUB_REPOS = [
    ("u-boot", "u-boot", "u-boot"),
    ("dosfstools", "dosfstools", "dosfstools"),
    ("bestouff", "genext2fs", "genext2fs"),
    ("plougher", "squashfs-tools", "squashfs-tools"),
    ("avahi", "avahi", "avahi"),
    ("inotify-tools", "inotify-tools", "inotify-tools"),
    ("hewlettpackard", "wireless-tools", "wireless-tools"),
    ("shadow-maint", "shadow", "shadow"),
    ("pupnp", "pupnp", "pupnp"),
    ("google", "brotli", "brotli"),
    ("libbpf", "bpftool", "bpftool"),
    ("sqlite", "sqlite", "sqlite"),
    ("llvm", "llvm-project", "llvm-project"),
    ("nixos", "nix", "nix"),
    ("miniupnp", "miniupnp", "miniupnp"),
    ("rpm-software-management", "rpm", "rpm"),
    ("python", "cpython", "cpython"),
    ("erofs", "erofs-utils", "erofs-utils"),
    ("openssl", "openssl", "openssl"),
]


def github_mock():

    for repo in GITHUB_REPOS:
        owner, name, subdir = repo

        directory = data_location / subdir
        if not os.path.exists(directory):
            os.makedirs(directory)

        url = f"https://api.github.com/repos/{owner}/{name}"
        response = get_response(url)
        mock_data_file = data_location / f"{subdir}/github_mock_data_0.json"

        with open(mock_data_file, "w") as json_file:
            json.dump(response, json_file, indent=2)

        fetch_github_mock_data(owner, name, subdir)


def main():
    github_mock()


if __name__ == "__main__":
    # Script to regenerate mock data for python_versions module.
    main()
