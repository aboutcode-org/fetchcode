"""Exceptions used throughout package"""

from itertools import groupby
from typing import TYPE_CHECKING, Dict, List

from fetchcode.vcs.pip._vendor.requests.models import Request, Response

if TYPE_CHECKING:
    from hashlib import _Hash

class PipError(Exception):
    """Base pip exception"""

class InstallationError(PipError):
    """General exception during installation"""


class BadCommand(PipError):
    """Raised when virtualenv or a command is not found"""


class CommandError(PipError):
    """Raised when there is an error in command-line arguments"""


class NetworkConnectionError(PipError):
    """HTTP connection error"""

    def __init__(self, error_msg, response=None, request=None):
        # type: (str, Response, Request) -> None
        """
        Initialize NetworkConnectionError with  `request` and `response`
        objects.
        """
        self.response = response
        self.request = request
        self.error_msg = error_msg
        if (self.response is not None and not self.request and
                hasattr(response, 'request')):
            self.request = self.response.request
        super().__init__(error_msg, response, request)

    def __str__(self):
        # type: () -> str
        return str(self.error_msg)


class InstallationSubprocessError(InstallationError):
    """A subprocess call failed during installation."""
    def __init__(self, returncode, description):
        # type: (int, str) -> None
        self.returncode = returncode
        self.description = description

    def __str__(self):
        # type: () -> str
        return (
            "Command errored out with exit status {}: {} "
            "Check the logs for full command output."
        ).format(self.returncode, self.description)


class HashErrors(InstallationError):
    """Multiple HashError instances rolled into one for reporting"""

    def __init__(self):
        # type: () -> None
        self.errors = []  # type: List[HashError]

    def append(self, error):
        # type: (HashError) -> None
        self.errors.append(error)

    def __str__(self):
        # type: () -> str
        lines = []
        self.errors.sort(key=lambda e: e.order)
        for cls, errors_of_cls in groupby(self.errors, lambda e: e.__class__):
            lines.append(cls.head)
            lines.extend(e.body() for e in errors_of_cls)
        if lines:
            return '\n'.join(lines)
        return ''

    def __nonzero__(self):
        # type: () -> bool
        return bool(self.errors)

    def __bool__(self):
        # type: () -> bool
        return self.__nonzero__()


class HashError(InstallationError):
    """
    A failure to verify a package against known-good hashes

    :cvar order: An int sorting hash exception classes by difficulty of
        recovery (lower being harder), so the user doesn't bother fretting
        about unpinned packages when he has deeper issues, like VCS
        dependencies, to deal with. Also keeps error reports in a
        deterministic order.
    :cvar head: A section heading for display in potentially many
        exceptions of this kind

    """
    head = ''
    order = -1  # type: int

    def __str__(self):
        # type: () -> str
        return f'{self.head}'


class VcsHashUnsupported(HashError):
    """A hash was provided for a version-control-system-based requirement, but
    we don't have a method for hashing those."""

    order = 0
    head = ("Can't verify hashes for these requirements because we don't "
            "have a way to hash version control repositories:")

