from functools import wraps
from kivy.app import App
from kivy.logger import Logger
from kivy.core.window import Window

# modes here are imported so that cache_manager can get them
from modes import fundamental  # noqa: F401  # pylint: disable=unused-import


modes_keymap = {
    'f': 'fundamental',
    'c': 'channel',
    'o': 'octave',
}


def mode_changer(_root, _keyboard, _scancode, codepoint, modifier):
    cm = App.get_running_app().cm
    if 'meta' in modifier:
        if codepoint in modes_keymap.keys():
            cm.major_mode = modes_keymap[codepoint]
        else:
            Logger.warning('kimidi.modes: %s mode not available (%s)', codepoint, modes_keymap.keys())
    return cm.major_mode


def key_down(func):
    @wraps(func)  # discussion about why wraps is required here https://github.com/kivy/kivy/issues/7007
    def _key_down(*args, **kwargs):
        major_mode = mode_changer(*args, **kwargs)
        major_mode.key_down(*args, **kwargs)
        func(*args, **kwargs)
    return _key_down


def key_up(func):
    @wraps(func)
    def _key_up(*args, **kwargs):
        major_mode = App.get_running_app().cm.major_mode
        major_mode.key_up(*args, **kwargs)
        func(*args, **kwargs)
    return _key_up


class KeyboardAdapter:
    def __init__(self, *_args, **_kwargs):
        self._keyboard = None

    def setup_keyboard(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)
        self._keyboard = None

    @key_down
    def on_key_down(self, _keyboard, _scancode, _codepoint, _modifier):
        pass

    @key_up
    def on_key_up(self, _keyboard, _scancode):
        pass
