# SPDX-License-Identifier: MIT
# Copyright @ The pip developers (see pip-AUTHORS.txt). All rights reserved

import os

from fetchcode.vcs.pip._internal.vcs.mercurial import Mercurial
from lib import _create_test_package, need_mercurial


@need_mercurial
def test_get_repository_root(script):
    version_pkg_path = _create_test_package(script, vcs="hg")
    tests_path = version_pkg_path.joinpath("tests")
    tests_path.mkdir()

    root1 = Mercurial.get_repository_root(version_pkg_path)
    assert os.path.normcase(root1) == os.path.normcase(version_pkg_path)

    root2 = Mercurial.get_repository_root(version_pkg_path.joinpath("tests"))
    assert os.path.normcase(root2) == os.path.normcase(version_pkg_path)
