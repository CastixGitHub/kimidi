"""Key concepts:
modes react to user inputs and are them that send the midi messages or make things happen on the screen,
them are a central point of this application
there are major modes and minor modes
you can activete only 1 major mode, and unlimted minor modes at the same time.
minor modes act before major mode and may change user input
so minor modes can conflict each other, when there might be a conflict, the conflictual one is deactivated

List of major modes:
- fundamental mode that allows you to send midi events with your keyboard and send cc events
- edit mode that allows you to edit controls and does not send anything
List of minor modes:
- channel allows you to select the channel/sreen
- octave allows you to rapidly get higher or lower notes from the keyboard (conflicts with channel)
"""
from functools import wraps
from kivy.app import App
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.event import EventDispatcher


# ================================================================================
# defining helpers to create modes


def int_max(v, _max=127):
    """converts to int if needed, ensures values are >= 0 <= 127 and channel >= 0 <=15,
    also avoid the app to crash when there is an error into the used mode"""
    if isinstance(v, (str, float)):
        v = int(v)
    if not isinstance(v, int):
        raise ValueError(v)
    if 0 > v <= _max:
        raise ValueError(v)
    return v


def safe_key_event(func):
    def _key(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            Logger.exception('kimidi.modes: key failed %s', e)
    return _key


def safe_cc(func):
    def _cc(w, cc, value, **kwargs):
        channel = kwargs.pop('channel', None)  # pylint: disable=redefined-outer-name # noqa: F811
        if channel is None and w and hasattr(w, 'channel'):  # autodetect from widgets
            channel = w.channel
        else:
            channel = App.get_running_app().cm.channel

        try:
            if channel is None:
                raise Exception('kimidi.modes.fundamental: cannot get channel in any way')
            cc = int_max(cc)
            channel = int_max(channel, _max=15)
            value = int_max(value)
            func(w, cc, value, channel=channel, **kwargs)
        except Exception:  # pylint: disable=broad-except
            Logger.exception('kimidi.modes:')
    return _cc


std_16_keymap = {
    **{str(i): i for i in range(10)},
    'q': 11, 'w': 12, 'e': 13, 'r': 14, 't': 15,
}


# ================================================================================
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


# ================================================================================
# now it's time to get midi cc events, them can be triggered
# by clicking, scrolling, keyboard or whatever
# currently edit mode supports widgets only

class MidiCCAdapter(EventDispatcher):
    """Inherited on every widget that sends midi cc events"""
    def __init__(self, *args, **kwargs):
        self.register_event_type('on_midi_cc')  # pylint: disable=not-callable
        super().__init__(*args, **kwargs)

    def on_midi_cc(self, cc, value, **kwargs):
        """
        channel is automatically detected, if the automatic detection fails, an error is logged.
        channel detection is available for widgets only, you can always override the channel used
        in kwargs like self.cc(64, channel=2)
        """
        cm = App.get_running_app().cm
        for minor_mode in cm.minor_modes:
            minor_mode.midi_cc(self, cc, value, **kwargs)
        cm.major_mode.midi_cc(self, cc, value, **kwargs)

    def cc(self, cc, value, **kwargs):  # just a shorthand
        self.dispatch('on_midi_cc', cc, value, **kwargs)

# TODO: make mode selection available through UI
# class ClickyModeSwitcher:
