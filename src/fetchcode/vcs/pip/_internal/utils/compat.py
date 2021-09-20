# SPDX-License-Identifier: MIT
# Copyright @ The pip developers (see pip-AUTHORS.txt). All rights reserved

"""Stuff that differs in different Python versions and platform
distributions."""

import logging
import os
import sys

__all__ = ["WINDOWS"]


logger = logging.getLogger(__name__)


# packages in the stdlib that may have installation metadata, but should not be
# considered 'installed'.  this theoretically could be determined based on
# dist.location (py27:`sysconfig.get_paths()['stdlib']`,
# py26:sysconfig.get_config_vars('LIBDEST')), but fear platform variation may
# make this ineffective, so hard-coding
stdlib_pkgs = {"python", "wsgiref", "argparse"}


# windows detection, covers cpython and ironpython
WINDOWS = sys.platform.startswith("win") or (sys.platform == "cli" and os.name == "nt")
