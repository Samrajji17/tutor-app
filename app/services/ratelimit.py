"""Tiny in-memory rate limiter.

It is per process, which is adequate for a single small site. If the site is
ever run with many workers, swap this for a shared store.
"""
import time
from collections import defaultdict, deque

_hits = defaultdict(deque)


def allow(key, limit, window):
    now = time.monotonic()
    hits = _hits[key]
    while hits and now - hits[0] > window:
        hits.popleft()
    if len(hits) >= limit:
        return False
    hits.append(now)
    return True


def reset():
    _hits.clear()
