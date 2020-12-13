# This file is part of KiMidi.

# KiMidi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# KiMidi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with KiMidi.  If not, see <https://www.gnu.org/licenses/>.

"""This isn't a real mode, but you can think it is (I didn't bother to do a new namespace)"""
# pylint: disable=unused-variable
from kivy.app import App
from kivy.logger import Logger
import time

import threading
try:
    import ipdb
    pdb = ipdb
except ImportError:
    import pdb  # or pdbpp if installed (drop-in replacement)
# this way we are also keeping compatibility with python 3.6 (by not using breakpoint())


def _target():  # pylint: disable=too-many-locals
    # wait app startup
    time.sleep(.5)

    # defining here a namespace pre-populated for locals()
    app = App.get_running_app()
    cm = app.cm
    sm = app.sm  # noqa: F841
    screens = app.sm.screens  # noqa: F841

    # modes
    major = major_mode = cm.major_mode  # noqa: F841
    major_name = major_mode_name = cm.major_mode_name  # noqa: F841
    minor = minor_modes = cm.minor_modes  # noqa: F841
    minor_name = minor_modes_names = cm.minor_modes_names  # noqa: F841

    # config/settings
    config = app.config
    sections = config.sections()  # noqa: F841

    def section_keys(name):
        return config.options(name)

    def section_values(name):
        return [config.get(name, opt) for opt in section_keys(name)]

    def section(name):
        return dict(zip(section_keys(name), section_values(name)))

    while True:   # this way you cant exit the debugger :P a new one is spawned  # you can in ipython tough
        # if you want to use python's help built-in use it like: !help(app)
        try:
            __import__('IPython').embed()
            # see also the 2011 bug https://github.com/ipython/ipython/issues/680
        except ImportError:
            if hasattr(pdb, 'interact'):
                pdb.interact()
            else:
                pdb.set_trace()
        # import IPython
        # IPython.terminal.interactiveshell.TerminalInteractiveShell.instance().simple_prompt = False
        # IPython.terminal.interactiveshell.TerminalInteractiveShell.instance().mainloop()
        # IPython.terminal.debugger.set_trace()
        # IPython.embed()


def enter_debug():
    Logger.debug('kimidi.modes.debug: DEBUG enabled, type locals() to get help')
    threading.Thread(target=_target, daemon=True).start()
