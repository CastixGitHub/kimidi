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
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.screenmanager import SlideTransition
import modes


@modes.safe_key_event
def key_down(_root, _keyboard, _scancode, codepoint, _modifier):
    Logger.debug('intention to switch to channel %s', codepoint)
    app = App.get_running_app()
    old = app.cm.channel
    try:
        new = modes.std_16_keymap[codepoint]
    except KeyError:
        new = None
        Logger.debug('kimidi.modes.channel: no action for %s', codepoint)
    if old != new and new is not None:
        app.sm.transition = SlideTransition(
            direction='right' if old - new > 0 else 'left'
        )
        for i, ch_name in enumerate(app.sm.screen_names):
            ch_number = int(app.config[f'channel {ch_name}']['number'])
            if ch_number == new:
                Logger.info('kimidi.root: switch to channel: %s number: %s', ch_name, ch_number)
                app.cm.channel = new
                app.sm.current = app.sm.screen_names[i]
                return


@modes.safe_key_event
def key_up(_root, _keyboard, _scancode):
    pass


@modes.safe_cc
def midi_cc(*a, **kw):
    pass
