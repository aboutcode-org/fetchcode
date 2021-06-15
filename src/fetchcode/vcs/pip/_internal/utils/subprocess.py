from __future__ import absolute_import

import logging
import os
import subprocess

from fetchcode.vcs.pip._vendor.six.moves import shlex_quote

from fetchcode.vcs.pip._internal.exceptions import InstallationError
from fetchcode.vcs.pip._internal.utils.compat import console_to_str, str_to_display
from fetchcode.vcs.pip._internal.utils.logging import subprocess_logger
from fetchcode.vcs.pip._internal.utils.misc import HiddenText, path_to_display


LOG_DIVIDER = '----------------------------------------'


def make_command(*args):
    # type: (Union[str, HiddenText, CommandArgs]) -> CommandArgs
    """
    Create a CommandArgs object.
    """
    command_args = []  # type: CommandArgs
    for arg in args:
        # Check for list instead of CommandArgs since CommandArgs is
        # only known during type-checking.
        if isinstance(arg, list):
            command_args.extend(arg)
        else:
            # Otherwise, arg is str or HiddenText.
            command_args.append(arg)

    return command_args


def format_command_args(args):
    # type: (Union[List[str], CommandArgs]) -> str
    """
    Format command arguments for display.
    """
    # For HiddenText arguments, display the redacted form by calling str().
    # Also, we don't apply str() to arguments that aren't HiddenText since
    # this can trigger a UnicodeDecodeError in Python 2 if the argument
    # has type unicode and includes a non-ascii character.  (The type
    # checker doesn't ensure the annotations are correct in all cases.)
    return ' '.join(
        shlex_quote(str(arg)) if isinstance(arg, HiddenText)
        else shlex_quote(arg) for arg in args
    )


def reveal_command_args(args):
    # type: (Union[List[str], CommandArgs]) -> List[str]
    """
    Return the arguments in their raw, unredacted form.
    """
    return [
        arg.secret if isinstance(arg, HiddenText) else arg for arg in args
    ]

