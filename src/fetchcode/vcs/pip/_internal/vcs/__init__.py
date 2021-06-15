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

# Expose a limited set of classes and functions so callers outside of
# the vcs package don't need to import deeper than `pip._internal.vcs`.
# (The test directory and imports protected by MYPY_CHECK_RUNNING may
# still need to import from a vcs sub-package.)
# Import all vcs modules to register each VCS in the VcsSupport object.
import fetchcode.vcs.pip._internal.vcs.bazaar
import fetchcode.vcs.pip._internal.vcs.git
import fetchcode.vcs.pip._internal.vcs.mercurial
import fetchcode.vcs.pip._internal.vcs.subversion  # noqa: F401
from fetchcode.vcs.pip._internal.vcs.versioncontrol import (  # noqa: F401
    RemoteNotFoundError,
    is_url,
    make_vcs_requirement_url,
    vcs,
)
