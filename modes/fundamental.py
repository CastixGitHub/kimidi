from kivy.app import App
from kivy.logger import Logger
from mido import Message

import modes


@modes.safe_key_event
def key_down(_root, _keyboard, _scancode, codepoint, _modifier):
    #         elif self.note_octave_selection:
    #             self.note_octave_selection = False
    #             self.app.cm.note_octave = int(text)
    cm = App.get_running_app().cm
    if codepoint in cm.keys.keys():
        if cm.activate_note(codepoint):
            msg = Message('note_on', note=cm.keys[codepoint],
                          velocity=64, channel=cm.channel)
            Logger.info(msg)
            App.get_running_app().cm.output.send(msg)


@modes.safe_key_event
def key_up(_root, _keyboard, scancode):
    cm = App.get_running_app().cm
    if scancode[1] in cm.keys.keys():
        if cm.release_note(scancode[1]):
            msg = Message('note_off', note=cm.keys[scancode[1]], velocity=64, channel=cm.channel)
            Logger.info(msg)
            App.get_running_app().cm.output.send(msg)


@modes.safe_cc
def midi_cc(_w, cc, value, **kwargs):
    cm = App.get_running_app().cm
    channel = kwargs.get('channel')
    msg = Message('control_change', control=cc, channel=channel, value=value)
    cm.output.send(msg)
    Logger.info(msg)
