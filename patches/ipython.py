# This file is part of KiMidi.

# KiMidi is free software; but this file is public domain
"""This module is here to patch IPython and make it work with trio
Huge thanks to mikenerone that shared this snippet
https://gist.github.com/mikenerone/786ce75cf8d906ae4ad1e0b57933c23f

The method exposed is ipython_worker, and should be used like
`await trio.to_thread.run_sync(ipython_worker)`
"""

from unittest.mock import patch

import IPython
import trio


def trio_embedded_runner(coro):
    return trio.from_thread.run(lambda: coro)


def ipython_worker(**kwargs):
    with IPythonAtExitContext():
        IPython.embed(using=trio_embedded_runner, **kwargs)


class IPythonAtExitContext:

    ipython_modules_with_atexit = [
        "IPython.core.magics.script",
        "IPython.core.application",
        "IPython.core.interactiveshell",
        "IPython.core.history",
        "IPython.utils.io",
    ]

    def __init__(self):
        self._calls = []
        self._patchers = []

    def __enter__(self):
        for module in self.ipython_modules_with_atexit:
            try:
                patcher = patch(module + ".atexit", self)
                patcher.start()
            except (AttributeError, ModuleNotFoundError):
                pass
            else:
                self._patchers.append(patcher)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for patcher in self._patchers:
            patcher.stop()
        self._patchers.clear()
        cb_exc = None
        for func, args, kwargs in self._calls:
            # noinspection PyBroadException
            try:
                func(*args, **kwargs)
            except Exception as _exc:
                cb_exc = _exc
        self._calls.clear()
        if cb_exc and not exc_type:
            raise cb_exc

    def register(self, func, *args, **kwargs):
        self._calls.append((func, args, kwargs))

    def unregister(self, func):
        self._calls = [call for call in self._calls if call[0] != func]
