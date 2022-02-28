# SPDX-License-Identifier: MIT
# Copyright @ The pip developers (see pip-AUTHORS.txt). All rights reserved

import os
import shutil
import sys

import pytest

from fetchcode.vcs.pip._internal.utils.temp_dir import global_tempdir_manager
from lib import VCSTestEnvironment
from lib.path import Path
from lib.compat import nullcontext


def pytest_addoption(parser):
    parser.addoption(
        "--keep-tmpdir",
        action="store_true",
        default=False,
        help="keep temporary test directories",
    )


@pytest.fixture(scope="session")
def tmpdir_factory(request, tmpdir_factory):
    """Modified `tmpdir_factory` session fixture
    that will automatically cleanup after itself.
    """
    yield tmpdir_factory
    if not request.config.getoption("--keep-tmpdir"):
        shutil.rmtree(
            tmpdir_factory.getbasetemp(),
            ignore_errors=True,
        )


@pytest.fixture
def tmpdir(request, tmpdir):
    """
    Return a temporary directory path object which is unique to each test
    function invocation, created as a sub directory of the base temporary
    directory. The returned object is a ``tests.lib.path.Path`` object.

    This uses the built-in tmpdir fixture from pytest itself but modified
    to return our typical path object instead of py.path.local as well as
    deleting the temporary directories at the end of each test case.
    """
    assert tmpdir.isdir()
    yield Path(str(tmpdir))
    # Clear out the temporary directory after the test has finished using it.
    # This should prevent us from needing a multiple gigabyte temporary
    # directory while running the tests.
    if not request.config.getoption("--keep-tmpdir"):
        tmpdir.remove(ignore_errors=True)


@pytest.fixture(autouse=True)
def isolate(tmpdir, monkeypatch):
    """
    Isolate our tests so that things like global configuration files and the
    like do not affect our test results.

    We use an autouse function scoped fixture because we want to ensure that
    every test has it's own isolated home directory.
    """

    # TODO: Figure out how to isolate from *system* level configuration files
    #       as well as user level configuration files.

    # Create a directory to use as our home location.
    home_dir = os.path.join(str(tmpdir), "home")
    os.makedirs(home_dir)

    # Create a directory to use as a fake root
    fake_root = os.path.join(str(tmpdir), "fake-root")
    os.makedirs(fake_root)

    if sys.platform == "win32":
        # Note: this will only take effect in subprocesses...
        home_drive, home_path = os.path.splitdrive(home_dir)
        monkeypatch.setenv("USERPROFILE", home_dir)
        monkeypatch.setenv("HOMEDRIVE", home_drive)
        monkeypatch.setenv("HOMEPATH", home_path)
        for env_var, sub_path in (
            ("APPDATA", "AppData/Roaming"),
            ("LOCALAPPDATA", "AppData/Local"),
        ):
            path = os.path.join(home_dir, *sub_path.split("/"))
            monkeypatch.setenv(env_var, path)
            os.makedirs(path)
    else:
        # Set our home directory to our temporary directory, this should force
        # all of our relative configuration files to be read from here instead
        # of the user's actual $HOME directory.
        monkeypatch.setenv("HOME", home_dir)

    # Configure git, because without an author name/email git will complain
    # and cause test failures.
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_AUTHOR_NAME", "pip")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "distutils-sig@python.org")

    # FIXME: Windows...
    with open(os.path.join(home_dir, ".gitconfig"), "wb") as fp:
        fp.write(b"[user]\n\tname = pip\n\temail = distutils-sig@python.org\n")


@pytest.fixture(autouse=True)
def scoped_global_tempdir_manager(request):
    """Make unit tests with globally-managed tempdirs easier

    Each test function gets its own individual scope for globally-managed
    temporary directories in the application.
    """
    if "no_auto_tempdir_manager" in request.keywords:
        ctx = nullcontext
    else:
        ctx = global_tempdir_manager

    with ctx():
        yield


@pytest.fixture(scope="session")
def script_factory():
    def factory(tmpdir):
        return VCSTestEnvironment(
            tmpdir,
            ignore_hidden=False,
            start_clear=False,
            capture_temp=True,
            assert_no_temp=True,
        )

    return factory


@pytest.fixture
def script(tmpdir, script_factory):
    """
    Return a PipTestEnvironment which is unique to each test function and
    will execute all commands inside of the unique virtual environment for this
    test function. The returned object is a
    ``tests.lib.PipTestEnvironment``.
    """
    return script_factory(tmpdir.joinpath("workspace"))
