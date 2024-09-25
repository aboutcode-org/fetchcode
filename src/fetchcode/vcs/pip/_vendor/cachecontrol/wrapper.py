# SPDX-FileCopyrightText: 2015 Eric Larson
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TYPE_CHECKING, Collection

from fetchcode.vcs.pip._vendor.cachecontrol.adapter import CacheControlAdapter
from fetchcode.vcs.pip._vendor.cachecontrol.cache import DictCache

if TYPE_CHECKING:
    from fetchcode.vcs.pip._vendor import requests

    from fetchcode.vcs.pip._vendor.cachecontrol.cache import BaseCache
    from fetchcode.vcs.pip._vendor.cachecontrol.controller import CacheController
    from fetchcode.vcs.pip._vendor.cachecontrol.heuristics import BaseHeuristic
    from fetchcode.vcs.pip._vendor.cachecontrol.serialize import Serializer


def CacheControl(
    sess: requests.Session,
    cache: BaseCache | None = None,
    cache_etags: bool = True,
    serializer: Serializer | None = None,
    heuristic: BaseHeuristic | None = None,
    controller_class: type[CacheController] | None = None,
    adapter_class: type[CacheControlAdapter] | None = None,
    cacheable_methods: Collection[str] | None = None,
) -> requests.Session:
    cache = DictCache() if cache is None else cache
    adapter_class = adapter_class or CacheControlAdapter
    adapter = adapter_class(
        cache,
        cache_etags=cache_etags,
        serializer=serializer,
        heuristic=heuristic,
        controller_class=controller_class,
        cacheable_methods=cacheable_methods,
    )
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)

    return sess
