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
from dateutil import parser as dateparser
import requests


def fetch_github_tags_gql(purl):
    """
    Yield PackageVersion for given github ``purl`` using the GitHub GQL API.
    """
    for node in fetch_github_tag_nodes(purl):
        name = node["name"]
        target = node["target"]

        # in case the tag is a signed tag, then the commit info is in target['target']
        if "committedDate" not in target:
            target = target["target"]

        committed_date = target.get("committedDate")
        release_date = None
        if committed_date:
            release_date = dateparser.parse(committed_date)

        yield name, release_date


GQL_QUERY = """
query getTags($name: String!, $owner: String!, $after: String)
{
    repository(name: $name, owner: $owner) {
        refs(refPrefix: "refs/tags/", first: 100, after: $after) {
            totalCount
            pageInfo {
                endCursor
                hasNextPage
            }
            nodes {
                name
                target {
                    ... on Commit {
                        committedDate
                    }
                    ... on Tag {
                            target {
                            ... on Commit {
                                committedDate
                            }
                        }
                    }
                }
            }
        }
    }
}"""


def fetch_github_tag_nodes(purl):
    """
    Yield node name/target mappings for Git tags of the ``purl``.

    Each node has this shape:
        {
        "name": "v2.6.24-rc5",
        "target": {
            "target": {
            "committedDate": "2007-12-11T03:48:43Z"
            }
        }
        },
    """
    variables = {
        "owner": purl.namespace,
        "name": purl.name,
    }
    graphql_query = {
        "query": GQL_QUERY,
        "variables": variables,
    }

    while True:
        response = github_response(graphql_query)
        refs = response["data"]["repository"]["refs"]
        for node in refs["nodes"]:
            yield node

        page_info = refs["pageInfo"]
        if not page_info["hasNextPage"]:
            break

        # to fetch next page, we just set the after variable to endCursor
        variables["after"] = page_info["endCursor"]


class GitHubTokenError(Exception):
    pass


class GraphQLError(Exception):
    pass


def github_response(graphql_query):
    gh_token = os.environ.get("GH_TOKEN", None)
    if not gh_token:
        from dotenv import load_dotenv

        load_dotenv()
        gh_token = os.environ.get("GH_TOKEN", None)

    if not gh_token:
        msg = (
            "GitHub API Token Not Set\n"
            "Set your GitHub token in the GH_TOKEN environment variable."
        )
        raise GitHubTokenError(msg)

    headers = {"Authorization": f"bearer {gh_token}"}

    endpoint = "https://api.github.com/graphql"
    response = requests.post(endpoint, headers=headers, json=graphql_query).json()

    message = response.get("message")
    if message and message == "Bad credentials":
        raise GitHubTokenError(f"Invalid GitHub token: {message}")

    errors = response.get("errors")
    if errors:
        raise GraphQLError(errors)

    return response
