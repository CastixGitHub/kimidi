from functools import wraps
from kivy.app import App
from kivy.logger import Logger
from kivy.core.window import Window


# ================================================================================
# defining helpers to create modes

def safe_key_event(func):
    def _key(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            Logger.exception(e)
    return _key


std_16_keymap = {
    **{str(i): i for i in range(10)},
    'q': 11, 'w': 12, 'e': 13, 'r': 14, 't': 15,
}


# modes here are imported so that cache_manager can get them
# must also be imported after safe_key_event to avoid circular dependency
from modes import fundamental  # noqa: F401, E402  # pylint: disable=unused-import,wrong-import-position
from modes import channel  # noqa: F401, E402  # pylint: disable=unused-import,wrong-import-position
from modes import edit  # noqa: F401, E402  # pylint: disable=unused-import,wrong-import-position


# ================================================================================
# now it's time to define utilities to switch modes and to handle the keys

major_modes_keymap = {
    'f': 'fundamental',
    'e': 'edit',
}

minor_modes_keymap = {
    'c': 'channel',
    'o': 'octave',
}


def minor_modes_conflicts(this):
    cm = App.get_running_app().cm
    for c in getattr(this, 'conflicts', []):
        cm.toggle_minor_mode(c, force=0)


class ModeChanged(Exception):
    pass


# these are modifiers, probably because of remapping?
weird_codepoints = ['ĵ', 'Ĵ', 'ı', None]


def mode_changer(_root, _keyboard, _scancode, codepoint, modifier):
    cm = App.get_running_app().cm
    if 'meta' in modifier:
        if codepoint in major_modes_keymap.keys():
            cm.major_mode = major_modes_keymap[codepoint]
            raise ModeChanged(f'Major mode {major_modes_keymap[codepoint]} activated')
        if codepoint in minor_modes_keymap.keys():
            state = cm.toggle_minor_mode(minor_modes_keymap[codepoint])
            raise ModeChanged(f'Minor mode {minor_modes_keymap[codepoint]} to {"ON" if state else "OFF"}')
        if codepoint not in weird_codepoints:
            Logger.warning('kimidi.modes: %s mode not available: %s', codepoint,
                           {**major_modes_keymap, **minor_modes_keymap})
    return cm.major_mode, cm.minor_modes


def key_down(func):
    @wraps(func)  # discussion about why wraps is required here https://github.com/kivy/kivy/issues/7007
    def _key_down(*args, **kwargs):
        try:
            major_mode, minor_modes = mode_changer(*args, **kwargs)
            for minor_mode in minor_modes:
                minor_mode.key_down(*args, **kwargs)
            major_mode.key_down(*args, **kwargs)
        except ModeChanged as i:
            Logger.info(str(i))
        func(*args, **kwargs)
    return _key_down


def key_up(func):
    @wraps(func)
    def _key_up(*args, **kwargs):
        try:
            major_mode = App.get_running_app().cm.major_mode
            major_mode.key_up(*args, **kwargs)
        except ModeChanged:
            pass
        func(*args, **kwargs)
    return _key_up


class KeyboardAdapter:
    """Inherited in root widget, gives it a keyboard full of features"""
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
