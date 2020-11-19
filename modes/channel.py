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
