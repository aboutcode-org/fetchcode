# SPDX-License-Identifier: MIT
# Copyright @ The pip developers (see pip-AUTHORS.txt). All rights reserved

import os
import re
import subprocess
import sys
import textwrap
from base64 import urlsafe_b64encode
from textwrap import dedent

import pytest
from scripttest import TestFileEnvironment

from lib.path import Path


def assert_paths_equal(actual, expected):
    assert os.path.normpath(actual) == os.path.normpath(expected)


def path_to_url(path):
    """
    Convert a path to URI. The path will be made absolute and
    will not have quoted path parts.
    (adapted from pip.util)
    """
    path = os.path.normpath(os.path.abspath(path))
    drive, path = os.path.splitdrive(path)
    filepath = path.split(os.path.sep)
    url = "/".join(filepath)
    if drive:
        # Note: match urllib.request.pathname2url's
        # behavior: uppercase the drive letter.
        return "file:///" + drive.upper() + url
    return "file://" + url


def _test_path_to_file_url(path):
    """
    Convert a test Path to a "file://" URL.

    Args:
      path: a tests.lib.path.Path object.
    """
    return "file://" + path.resolve().replace("\\", "/")


def create_file(path, contents=None):
    """Create a file on the path, with the given contents"""
    from fetchcode.vcs.pip._internal.utils.misc import ensure_dir

    ensure_dir(os.path.dirname(path))
    with open(path, "w") as f:
        if contents is not None:
            f.write(contents)
        else:
            f.write("\n")


class TestFailure(AssertionError):
    """
    An "assertion" failed during testing.
    """

    pass


class TestPipResult:
    def __init__(self, impl, verbose=False):
        self._impl = impl

        if verbose:
            print(self.stdout)
            if self.stderr:
                print("======= stderr ========")
                print(self.stderr)
                print("=======================")

    def __getattr__(self, attr):
        return getattr(self._impl, attr)

    if sys.platform == "win32":

        @property
        def stdout(self):
            return self._impl.stdout.replace("\r\n", "\n")

        @property
        def stderr(self):
            return self._impl.stderr.replace("\r\n", "\n")

        def __str__(self):
            return str(self._impl).replace("\r\n", "\n")

    else:
        # Python doesn't automatically forward __str__ through __getattr__

        def __str__(self):
            return str(self._impl)

    def did_create(self, path, message=None):
        assert str(path) in self.files_created, _one_or_both(message, self)

    def did_not_create(self, path, message=None):
        assert str(path) not in self.files_created, _one_or_both(message, self)

    def did_update(self, path, message=None):
        assert str(path) in self.files_updated, _one_or_both(message, self)

    def did_not_update(self, path, message=None):
        assert str(path) not in self.files_updated, _one_or_both(message, self)


def _one_or_both(a, b):
    """Returns f"{a}\n{b}" if a is truthy, else returns str(b)."""
    if not a:
        return str(b)

    return f"{a}\n{b}"


def make_check_stderr_message(stderr, line, reason):
    """
    Create an exception message to use inside check_stderr().
    """
    return dedent(
        """\
    {reason}:
     Caused by line: {line!r}
     Complete stderr: {stderr}
    """
    ).format(stderr=stderr, line=line, reason=reason)


def _check_stderr(
    stderr,
    allow_stderr_warning,
    allow_stderr_error,
):
    """
    Check the given stderr for logged warnings and errors.

    :param stderr: stderr output as a string.
    :param allow_stderr_warning: whether a logged warning (or deprecation
        message) is allowed. Must be True if allow_stderr_error is True.
    :param allow_stderr_error: whether a logged error is allowed.
    """
    assert not (allow_stderr_error and not allow_stderr_warning)

    lines = stderr.splitlines()
    for line in lines:
        # First check for logging errors, which we don't allow during
        # tests even if allow_stderr_error=True (since a logging error
        # would signal a bug in pip's code).
        #    Unlike errors logged with logger.error(), these errors are
        # sent directly to stderr and so bypass any configured log formatter.
        # The "--- Logging error ---" string is used in Python 3.4+, and
        # "Logged from file " is used in Python 2.
        if line.startswith("--- Logging error ---") or line.startswith(
            "Logged from file "
        ):
            reason = "stderr has a logging error, which is never allowed"
            msg = make_check_stderr_message(stderr, line=line, reason=reason)
            raise RuntimeError(msg)
        if allow_stderr_error:
            continue

        if line.startswith("ERROR: "):
            reason = (
                "stderr has an unexpected error "
                "(pass allow_stderr_error=True to permit this)"
            )
            msg = make_check_stderr_message(stderr, line=line, reason=reason)
            raise RuntimeError(msg)
        if allow_stderr_warning:
            continue

        if line.startswith("WARNING: "):
            reason = (
                "stderr has an unexpected warning "
                "(pass allow_stderr_warning=True to permit this)"
            )
            msg = make_check_stderr_message(stderr, line=line, reason=reason)
            raise RuntimeError(msg)


class VCSTestEnvironment(TestFileEnvironment):
    verbose = False

    def __init__(self, base_path, *args, **kwargs):
        base_path = Path(base_path)
        # Create a Directory to use as a scratch pad
        self.scratch_path = base_path.joinpath("scratch")

        kwargs.setdefault("cwd", self.scratch_path)
        kwargs.setdefault("environ", os.environ.copy())
        super().__init__(base_path, *args, **kwargs)
        self.scratch_path.mkdir()
        # Make sure temp_path is a Path object
        self.temp_path = Path(self.temp_path)
        # Ensure the tmp dir exists, things break horribly if it doesn't
        self.temp_path.mkdir()

    def run(
        self,
        *args,
        cwd=None,
        run_from=None,
        allow_stderr_error=None,
        allow_stderr_warning=None,
        allow_error=None,
        **kw,
    ):
        """
        :param allow_stderr_error: whether a logged error is allowed in
            stderr.  Passing True for this argument implies
            `allow_stderr_warning` since warnings are weaker than errors.
        :param allow_stderr_warning: whether a logged warning (or
            deprecation message) is allowed in stderr.
        :param allow_error: if True (default is False) does not raise
            exception when the command exit value is non-zero.  Implies
            expect_error, but in contrast to expect_error will not assert
            that the exit value is zero.
        :param expect_error: if False (the default), asserts that the command
            exits with 0.  Otherwise, asserts that the command exits with a
            non-zero exit code.  Passing True also implies allow_stderr_error
            and allow_stderr_warning.
        :param expect_stderr: whether to allow warnings in stderr (equivalent
            to `allow_stderr_warning`).  This argument is an abbreviated
            version of `allow_stderr_warning` and is also kept for backwards
            compatibility.
        """
        if self.verbose:
            print(f">> running {args} {kw}")

        assert not cwd or not run_from, "Don't use run_from; it's going away"
        cwd = cwd or run_from or self.cwd
        if sys.platform == "win32":
            # Partial fix for ScriptTest.run using `shell=True` on Windows.
            args = [str(a).replace("^", "^^").replace("&", "^&") for a in args]

        if allow_error:
            kw["expect_error"] = True

        # Propagate default values.
        expect_error = kw.get("expect_error")
        if expect_error:
            # Then default to allowing logged errors.
            if allow_stderr_error is not None and not allow_stderr_error:
                raise RuntimeError(
                    "cannot pass allow_stderr_error=False with expect_error=True"
                )
            allow_stderr_error = True

        elif kw.get("expect_stderr"):
            # Then default to allowing logged warnings.
            if allow_stderr_warning is not None and not allow_stderr_warning:
                raise RuntimeError(
                    "cannot pass allow_stderr_warning=False with expect_stderr=True"
                )
            allow_stderr_warning = True

        if allow_stderr_error:
            if allow_stderr_warning is not None and not allow_stderr_warning:
                raise RuntimeError(
                    "cannot pass allow_stderr_warning=False with "
                    "allow_stderr_error=True"
                )

        # Default values if not set.
        if allow_stderr_error is None:
            allow_stderr_error = False
        if allow_stderr_warning is None:
            allow_stderr_warning = allow_stderr_error

        # Pass expect_stderr=True to allow any stderr.  We do this because
        # we do our checking of stderr further on in check_stderr().
        kw["expect_stderr"] = True
        result = super().run(cwd=cwd, *args, **kw)

        if expect_error and not allow_error:
            if result.returncode == 0:
                __tracebackhide__ = True
                raise AssertionError("Script passed unexpectedly.")

        _check_stderr(
            result.stderr,
            allow_stderr_error=allow_stderr_error,
            allow_stderr_warning=allow_stderr_warning,
        )

        return TestPipResult(result, verbose=self.verbose)


# FIXME ScriptTest does something similar, but only within a single
# ProcResult; this generalizes it so states can be compared across
# multiple commands.  Maybe should be rolled into ScriptTest?
def diff_states(start, end, ignore=None):
    """
    Differences two "filesystem states" as represented by dictionaries
    of FoundFile and FoundDir objects.

    Returns a dictionary with following keys:

    ``deleted``
        Dictionary of files/directories found only in the start state.

    ``created``
        Dictionary of files/directories found only in the end state.

    ``updated``
        Dictionary of files whose size has changed (FIXME not entirely
        reliable, but comparing contents is not possible because
        FoundFile.bytes is lazy, and comparing mtime doesn't help if
        we want to know if a file has been returned to its earlier
        state).

    Ignores mtime and other file attributes; only presence/absence and
    size are considered.

    """
    ignore = ignore or []

    def prefix_match(path, prefix):
        if path == prefix:
            return True
        prefix = prefix.rstrip(os.path.sep) + os.path.sep
        return path.startswith(prefix)

    start_keys = {
        k for k in start.keys() if not any([prefix_match(k, i) for i in ignore])
    }
    end_keys = {k for k in end.keys() if not any([prefix_match(k, i) for i in ignore])}
    deleted = {k: start[k] for k in start_keys.difference(end_keys)}
    created = {k: end[k] for k in end_keys.difference(start_keys)}
    updated = {}
    for k in start_keys.intersection(end_keys):
        if start[k].size != end[k].size:
            updated[k] = end[k]
    return dict(deleted=deleted, created=created, updated=updated)


def assert_all_changes(start_state, end_state, expected_changes):
    """
    Fails if anything changed that isn't listed in the
    expected_changes.

    start_state is either a dict mapping paths to
    scripttest.[FoundFile|FoundDir] objects or a TestPipResult whose
    files_before we'll test.  end_state is either a similar dict or a
    TestPipResult whose files_after we'll test.

    Note: listing a directory means anything below
    that directory can be expected to have changed.
    """
    __tracebackhide__ = True

    start_files = start_state
    end_files = end_state
    if isinstance(start_state, TestPipResult):
        start_files = start_state.files_before
    if isinstance(end_state, TestPipResult):
        end_files = end_state.files_after

    diff = diff_states(start_files, end_files, ignore=expected_changes)
    if list(diff.values()) != [{}, {}, {}]:
        raise TestFailure(
            "Unexpected changes:\n"
            + "\n".join([k + ": " + ", ".join(v.keys()) for k, v in diff.items()])
        )

    # Don't throw away this potentially useful information
    return diff


def _create_main_file(dir_path, name=None, output=None):
    """
    Create a module with a main() function that prints the given output.
    """
    if name is None:
        name = "version_pkg"
    if output is None:
        output = "0.1"
    text = textwrap.dedent(
        f"""
        def main():
            print({output!r})
        """
    )
    filename = f"{name}.py"
    dir_path.joinpath(filename).write_text(text)


def _git_commit(
    env_or_script,
    repo_dir,
    message=None,
    allow_empty=False,
    stage_modified=False,
):
    """
    Run git-commit.

    Args:
      env_or_script: pytest's `script` or `env` argument.
      repo_dir: a path to a Git repository.
      message: an optional commit message.
    """
    if message is None:
        message = "test commit"

    args = []

    if allow_empty:
        args.append("--allow-empty")

    if stage_modified:
        args.append("--all")

    new_args = [
        "git",
        "commit",
        "-q",
        "--author",
        "pip <distutils-sig@python.org>",
    ]
    new_args.extend(args)
    new_args.extend(["-m", message])
    env_or_script.run(*new_args, cwd=repo_dir)


def _vcs_add(script, version_pkg_path, vcs="git"):
    if vcs == "git":
        script.run("git", "init", cwd=version_pkg_path)
        script.run("git", "add", ".", cwd=version_pkg_path)
        _git_commit(script, version_pkg_path, message="initial version")
    elif vcs == "hg":
        script.run("hg", "init", cwd=version_pkg_path)
        script.run("hg", "add", ".", cwd=version_pkg_path)
        script.run(
            "hg",
            "commit",
            "-q",
            "--user",
            "pip <distutils-sig@python.org>",
            "-m",
            "initial version",
            cwd=version_pkg_path,
        )
    elif vcs == "svn":
        repo_url = _create_svn_repo(script, version_pkg_path)
        script.run(
            "svn", "checkout", repo_url, "pip-test-package", cwd=script.scratch_path
        )
        checkout_path = script.scratch_path / "pip-test-package"

        # svn internally stores windows drives as uppercase; we'll match that.
        checkout_path = checkout_path.replace("c:", "C:")

        version_pkg_path = checkout_path
    elif vcs == "bazaar":
        script.run("bzr", "init", cwd=version_pkg_path)
        script.run("bzr", "add", ".", cwd=version_pkg_path)
        script.run(
            "bzr", "whoami", "pip <distutils-sig@python.org>", cwd=version_pkg_path
        )
        script.run(
            "bzr",
            "commit",
            "-q",
            "--author",
            "pip <distutils-sig@python.org>",
            "-m",
            "initial version",
            cwd=version_pkg_path,
        )
    else:
        raise ValueError(f"Unknown vcs: {vcs}")
    return version_pkg_path


def _create_test_package(script, name="version_pkg", vcs="git"):
    script.scratch_path.joinpath(name).mkdir()
    version_pkg_path = script.scratch_path / name
    _create_main_file(version_pkg_path, name=name, output="0.1")
    version_pkg_path.joinpath("setup.py").write_text(
        textwrap.dedent(
            """
                from setuptools import setup, find_packages
                setup(
                    name="{name}",
                    version="0.1",
                    packages=find_packages(),
                    py_modules=["{name}"],
                    entry_points=dict(console_scripts=["{name}={name}:main"]),
                )
            """.format(
                name=name
            )
        )
    )
    return _vcs_add(script, version_pkg_path, vcs)


def _create_svn_repo(script, version_pkg_path):
    repo_url = path_to_url(script.scratch_path / "pip-test-package-repo" / "trunk")
    script.run("svnadmin", "create", "pip-test-package-repo", cwd=script.scratch_path)
    script.run(
        "svn",
        "import",
        version_pkg_path,
        repo_url,
        "-m",
        "Initial import of pip-test-package",
        cwd=script.scratch_path,
    )
    return repo_url


def _change_test_package_version(script, version_pkg_path):
    _create_main_file(
        version_pkg_path, name="version_pkg", output="some different version"
    )
    # Pass -a to stage the change to the main file.
    _git_commit(script, version_pkg_path, message="messed version", stage_modified=True)


def assert_raises_regexp(exception, reg, run, *args, **kwargs):
    """Like assertRaisesRegexp in unittest"""
    __tracebackhide__ = True

    try:
        run(*args, **kwargs)
        assert False, f"{exception} should have been thrown"
    except exception:
        e = sys.exc_info()[1]
        p = re.compile(reg)
        assert p.search(str(e)), str(e)


def urlsafe_b64encode_nopad(data):
    # type: (bytes) -> str
    return urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def need_executable(name, check_cmd):
    def wrapper(fn):
        try:
            subprocess.check_output(check_cmd)
        except (OSError, subprocess.CalledProcessError):
            return pytest.mark.skip(reason=f"{name} is not available")(fn)
        return fn

    return wrapper


def is_bzr_installed():
    try:
        subprocess.check_output(("bzr", "version", "--short"))
    except OSError:
        return False
    return True


def is_svn_installed():
    try:
        subprocess.check_output(("svn", "--version"))
    except OSError:
        return False
    return True


def need_bzr(fn):
    return pytest.mark.bzr(need_executable("Bazaar", ("bzr", "version", "--short"))(fn))


def need_svn(fn):
    return pytest.mark.svn(
        need_executable("Subversion", ("svn", "--version"))(
            need_executable("Subversion Admin", ("svnadmin", "--version"))(fn)
        )
    )


def need_mercurial(fn):
    return pytest.mark.mercurial(need_executable("Mercurial", ("hg", "version"))(fn))
