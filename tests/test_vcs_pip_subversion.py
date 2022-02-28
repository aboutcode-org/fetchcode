# SPDX-License-Identifier: MIT
# Copyright @ The pip developers (see pip-AUTHORS.txt). All rights reserved

import pytest

from fetchcode.vcs.pip._internal.vcs.subversion import Subversion
from fetchcode.vcs.pip._internal.vcs.versioncontrol import RemoteNotFoundError
from lib import _create_svn_repo, need_svn


@need_svn
def test_get_remote_url__no_remote(script, tmpdir):
    repo_dir = tmpdir / "temp-repo"
    repo_dir.mkdir()
    repo_dir = str(repo_dir)

    _create_svn_repo(script, repo_dir)

    with pytest.raises(RemoteNotFoundError):
        Subversion().get_remote_url(repo_dir)


@need_svn
def test_get_remote_url__no_remote_with_setup(script, tmpdir):
    repo_dir = tmpdir / "temp-repo"
    repo_dir.mkdir()
    setup = repo_dir / "setup.py"
    setup.touch()
    repo_dir = str(repo_dir)

    _create_svn_repo(script, repo_dir)

    with pytest.raises(RemoteNotFoundError):
        Subversion().get_remote_url(repo_dir)
