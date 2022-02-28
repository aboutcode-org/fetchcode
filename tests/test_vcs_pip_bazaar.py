# SPDX-License-Identifier: MIT
# Copyright @ The pip developers (see pip-AUTHORS.txt). All rights reserved

"""
Contains functional tests of the Bazaar class.
"""

import os

import pytest

from fetchcode.vcs.pip._internal.vcs.bazaar import Bazaar
from fetchcode.vcs.pip._internal.vcs.versioncontrol import RemoteNotFoundError
from lib import is_bzr_installed, need_bzr


@pytest.mark.skipif(
    "CI" not in os.environ, reason="Bazaar is only required under CI"
)
def test_ensure_bzr_available():
    """Make sure that bzr is available when running in Travis."""
    assert is_bzr_installed()


@need_bzr
def test_get_remote_url__no_remote(script, tmpdir):
    repo_dir = tmpdir / "temp-repo"
    repo_dir.mkdir()
    repo_dir = str(repo_dir)

    script.run("bzr", "init", repo_dir)

    with pytest.raises(RemoteNotFoundError):
        Bazaar().get_remote_url(repo_dir)
