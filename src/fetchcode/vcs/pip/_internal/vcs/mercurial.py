# Copyright (c) 2008-2020 The pip developers:
# barneygale, Barney Gale, Chris Hunt, Chris Jerdonek, Christopher Hunt,
# Deepak Sharma, Devesh Kumar Singh, Donald Stufft, Dustin Ingram, Emil Burzo,
# Giftlin Rajaiah, Jason R. Coombs, Jelmer Vernooĳ, Jeremy Zafran, johnthagen,
# Jon Dufresne, Maxim Kurnikov, Nitesh Sharma, Pi Delport, Pradyun Gedam,
# Pradyun S. Gedam, Riccardo Magliocchetti, Shlomi Fish,
# Stéphane Bidoul (ACSONE), tbeswick, Tom Forbes, Tony Beswick, TonyBeswick,
# Tzu-ping Chung
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import

import logging
import os

from fetchcode.vcs.pip._vendor.six.moves import configparser

from fetchcode.vcs.pip._internal.exceptions import BadCommand, InstallationError
from fetchcode.vcs.pip._internal.utils.misc import display_path
from fetchcode.vcs.pip._internal.utils.subprocess import make_command
from fetchcode.vcs.pip._internal.utils.temp_dir import TempDirectory
from fetchcode.vcs.pip._internal.utils.urls import path_to_url
from fetchcode.vcs.pip._internal.vcs.versioncontrol import (
    VersionControl,
    find_path_to_setup_from_repo_root,
    vcs,
)


logger = logging.getLogger(__name__)


class Mercurial(VersionControl):
    name = 'hg'
    dirname = '.hg'
    repo_name = 'clone'
    schemes = (
        'hg', 'hg+file', 'hg+http', 'hg+https', 'hg+ssh', 'hg+static-http',
    )

    @staticmethod
    def get_base_rev_args(rev):
        return [rev]

    def export(self, location, url):
        # type: (str, HiddenText) -> None
        """Export the Hg repository at the url to the destination location"""
        with TempDirectory(kind="export") as temp_dir:
            self.unpack(temp_dir.path, url=url)

            self.run_command(
                ['archive', location], show_stdout=False, cwd=temp_dir.path
            )

    def fetch_new(self, dest, url, rev_options):
        # type: (str, HiddenText, RevOptions) -> None
        rev_display = rev_options.to_display()
        logger.info(
            'Cloning hg %s%s to %s',
            url,
            rev_display,
            display_path(dest),
        )
        self.run_command(make_command('clone', '--noupdate', '-q', url, dest))
        self.run_command(
            make_command('update', '-q', rev_options.to_args()),
            cwd=dest,
        )

    def switch(self, dest, url, rev_options):
        # type: (str, HiddenText, RevOptions) -> None
        repo_config = os.path.join(dest, self.dirname, 'hgrc')
        config = configparser.RawConfigParser()
        try:
            config.read(repo_config)
            config.set('paths', 'default', url.secret)
            with open(repo_config, 'w') as config_file:
                config.write(config_file)
        except (OSError, configparser.NoSectionError) as exc:
            logger.warning(
                'Could not switch Mercurial repository to %s: %s', url, exc,
            )
        else:
            cmd_args = make_command('update', '-q', rev_options.to_args())
            self.run_command(cmd_args, cwd=dest)

    def update(self, dest, url, rev_options):
        # type: (str, HiddenText, RevOptions) -> None
        self.run_command(['pull', '-q'], cwd=dest)
        cmd_args = make_command('update', '-q', rev_options.to_args())
        self.run_command(cmd_args, cwd=dest)

    @classmethod
    def get_remote_url(cls, location):
        url = cls.run_command(
            ['showconfig', 'paths.default'],
            show_stdout=False, cwd=location).strip()
        if cls._is_local_repository(url):
            url = path_to_url(url)
        return url.strip()

    @classmethod
    def get_revision(cls, location):
        """
        Return the repository-local changeset revision number, as an integer.
        """
        current_revision = cls.run_command(
            ['parents', '--template={rev}'],
            show_stdout=False, cwd=location).strip()
        return current_revision

    @classmethod
    def get_requirement_revision(cls, location):
        """
        Return the changeset identification hash, as a 40-character
        hexadecimal string
        """
        current_rev_hash = cls.run_command(
            ['parents', '--template={node}'],
            show_stdout=False, cwd=location).strip()
        return current_rev_hash

    @classmethod
    def is_commit_id_equal(cls, dest, name):
        """Always assume the versions don't match"""
        return False

    @classmethod
    def get_subdirectory(cls, location):
        """
        Return the path to setup.py, relative to the repo root.
        Return None if setup.py is in the repo root.
        """
        # find the repo root
        repo_root = cls.run_command(
            ['root'], show_stdout=False, cwd=location).strip()
        if not os.path.isabs(repo_root):
            repo_root = os.path.abspath(os.path.join(location, repo_root))
        return find_path_to_setup_from_repo_root(location, repo_root)

    @classmethod
    def get_repository_root(cls, location):
        loc = super(Mercurial, cls).get_repository_root(location)
        if loc:
            return loc
        try:
            r = cls.run_command(
                ['root'],
                cwd=location,
                show_stdout=False,
                on_returncode='raise',
                log_failed_cmd=False,
            )
        except BadCommand:
            logger.debug("could not determine if %s is under hg control "
                         "because hg is not available", location)
            return None
        except InstallationError:
            return None
        return os.path.normpath(r.rstrip('\r\n'))


vcs.register(Mercurial)
