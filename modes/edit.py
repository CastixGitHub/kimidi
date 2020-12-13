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
from kivy.uix.popup import Popup
from kivy.uix.settings import SettingsWithNoMenu
from kivy.input.providers.mouse import MouseMotionEvent

from widgets.namedpanel import NamedPanel
from settings import control
import modes


@modes.safe_key_event
def key_down(_root, _keyboard, _scancode, _codepoint, _modifier):
    pass


@modes.safe_key_event
def key_up(_root, _keyboard, _scancode):
    pass


class EditableModeOn(Exception):
    """This indicates to the widget that editable mode is on, so there is no need to update the UI"""


def prevent_when_edit(func):
    def _prevent(*args, **kwargs):
        prevent = False
        cm = App.get_running_app().cm
        if cm.major_mode.__name__ == 'modes.edit':
            if len(args) == 1:
                prevent = True
            elif isinstance(args[1], MouseMotionEvent) and args[0].collide_point(*args[1].pos):
                prevent = True

        if prevent:
            try:
                args[0].cc(0, 0)
            except EditableModeOn:
                return
        return func(*args, **kwargs)
    return _prevent


# @modes.safe_cc  # This is a special mode, handles exceptions on itself and propagate a custom exception
def midi_cc(w, _cc, _value, **kwargs):
    try:
        app = App.get_running_app()
        parent = w.parent
        try:
            while not isinstance(parent, NamedPanel):
                parent = parent.parent
        except AttributeError:
            Logger.error('kimidi.midieditable: cannot get parent of {w.name}')
        panel = parent  # clarify following code
        print(app, parent)
        settings = SettingsWithNoMenu()
        settings.add_json_panel(
            'These settings are immediatly applied and saved, click outside to close',
            app.config,
            data=control.dumps_single(panel, w.name)
        )
        popup = Popup(
            title=f'Editing: {w.name} on panel: {panel}',
            content=settings,
            size_hint=(.8, .8),
        )
        popup.bind(on_dismiss=App.get_running_app().on_settings_close)
        popup.open()

        raise EditableModeOn('on %s' % w.name)
    except EditableModeOn:
        raise  # this is the only exception that is propagated to the widget, where you should use @prevent_when_edit
    except Exception:  # pylint: disable=broad-except
        Logger.exception('kimidi.modes.edit: unknown exception')
