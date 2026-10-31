# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See https://github.com/aboutcode-org/fetchcode for support or download.

import pytest


@pytest.fixture(autouse=True)
def no_live_http_requests(monkeypatch):
    """Require HTTP responses to be mocked so unit tests also run offline."""

    def fail_on_request(self, method, url, **kwargs):
        pytest.fail(f"Unexpected live HTTP request: {method} {url}")

    monkeypatch.setattr("requests.sessions.Session.request", fail_on_request)
