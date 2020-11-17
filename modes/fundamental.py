from kivy.app import App
from kivy.logger import Logger
from mido import Message


def key_down(_root, _keyboard, _scancode, codepoint, _modifier):
    # if text and text.isdigit():
    #     if self.channel_selection:
    #         print('intention to switch to channel ' + text)
    #         self.channel_selection = False
    #         old = self.app.cm.channel
    #         if old != int(text):
    #             self.app.sm.transition = SlideTransition(
    #                 direction='right' if old - int(text) > 0 else 'left'
    #             )
    #             for i, ch_name in enumerate(self.app.sm.screen_names):
    #                 ch_number = int(self.app.config[f'channel {ch_name}']['number'])
    #                 if ch_number == int(text):
    #                     Logger.info('kimidi.root: switch to channel: %s number: %s', ch_name, ch_number)
    #                     self.app.cm.channel = int(text)
    #                     self.app.sm.current = self.app.sm.screen_names[i]
    #         elif self.note_octave_selection:
    #             self.note_octave_selection = False
    #             self.app.cm.note_octave = int(text)
    cm = App.get_running_app().cm
    if codepoint in cm.keys.keys():
        if codepoint not in cm.active_notes:
            cm.activate_note(codepoint)
            msg = Message('note_on', note=cm.keys[codepoint],
                          velocity=64, channel=cm.channel)
            Logger.info(msg)
            App.get_running_app().cm.output.send(msg)


def key_up(_root, _keyboard, scancode):
    cm = App.get_running_app().cm
    if scancode[1] in cm.keys.keys():
        cm.release_note(scancode[1])
        msg = Message('note_off', note=cm.keys[scancode[1]], velocity=64, channel=cm.channel)
        Logger.info(msg)
        App.get_running_app().cm.output.send(msg)
