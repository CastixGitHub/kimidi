"""KiMidi application entry point"""
# pylint: disable=wrong-import-position
import os
import argparse
os.environ["KIVY_NO_ARGS"] = "1"
from kivy.lang import Builder  # noqa: E402
from kivy.logger import Logger  # noqa: E402
from kivy.app import App  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.uix.settings import SettingsWithSidebar  # noqa: E402
from kivy.uix.gridlayout import GridLayout  # noqa: E402
from kivy.uix.floatlayout import FloatLayout  # noqa: E402
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition  # noqa: E402
from kivy.uix.button import Button  # noqa: E402
from kivy.properties import BooleanProperty  # noqa: E402
from mido import open_output, Message  # noqa: E402
import settings  # noqa: E402
import cache_manager as cm  # noqa: E402

output = open_output()


Builder.load_string("""
<Root>:
    Button:
        text: 'settings'
        font_size: 20
        pos: [root.width - self.width - 10, root.height - self.height - 10]
        size_hint: None, None
        size: 80, 30
        on_release: app.open_settings()
""", filename='Root.kv')


class Root(FloatLayout):
    channel_selection = BooleanProperty(False)
    note_octave_selection = BooleanProperty(False)

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.add_widget(self.app.sm)
        self._keyboard = None  # will be initialized by init_screens called by render...
        self.render()

    def init_screens(self):
        # also setup the keyboard, as can be closed by the settings
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)

        current = self.app.sm.current
        self.app.sm.clear_widgets()
        for channel_name in settings.names_of.channels(self.app.config):
            Logger.info('kimidi.root: adding channel %s', channel_name)
            screen = Screen(name=channel_name)
            screen.add_widget(Main(self.app, channel_name))  # kwargs should be passed
            self.app.sm.add_widget(screen)
        if len(settings.names_of.channels(self.app.config)) == 0:
            Logger.warning(
                'kimidi.root: your config is empty,'
                ' use --config-file option or go to'
                ' settings and create a channel to start with'
            )
            empty_screen = Screen(name='KIMIDI Empty Config')
            btn = Button(text='Settings', font_size=48, on_release=self.app.open_settings)
            btn.render = lambda: 0
            empty_screen.add_widget(btn)
            self.app.sm.add_widget(empty_screen)

        if current in self.app.sm.screen_names:
            self.app.sm.current = current

    def render(self):
        # assuming there is only one Main widget inside a screen
        self.init_screens()
        main = self.app.sm.current_screen.children[0]
        # main.channel_name = self.app.sm.current
        main.render()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)
        self._keyboard = None

    def on_key_down(self, keyboard, keycode, text, modifiers):
        if 'meta' in modifiers and text == 'c':
            self.channel_selection = True
        elif 'meta' in modifiers and text == 'o':
            self.note_octave_selection = True
        elif text and text.isdigit():
            if self.channel_selection:
                print('intention to switch to channel ' + text)
                self.channel_selection = False
                old = self.app.cm.channel
                if old != int(text):
                    self.app.sm.transition = SlideTransition(
                        direction='right' if old - int(text) > 0 else 'left'
                    )
                    for i, ch_name in enumerate(self.app.sm.screen_names):
                        ch_number = int(self.app.config[f'channel {ch_name}']['number'])
                        if ch_number == int(text):
                            Logger.info('kimidi.root: switch to channel: %s number: %s', ch_name, ch_number)
                            self.app.cm.channel = int(text)
                            self.app.sm.current = self.app.sm.screen_names[i]
            elif self.note_octave_selection:
                self.note_octave_selection = False
                self.app.cm.note_octave = int(text)
        elif text in self.app.cm.keys.keys():
            msg = Message('note_on', note=self.app.cm.keys[text], velocity=64, channel=self.app.cm.channel)
            Logger.info(msg)
            output.send(msg)

    def on_key_up(self, key, scancode=None, codepoint=None, modifier=None, **kwargs):
        if scancode[1] in self.app.cm.keys.keys()\
           and not self.channel_selection\
           and not self.note_octave_selection:
            msg = Message('note_off', note=self.app.cm.keys[scancode[1]], velocity=64, channel=self.app.cm.channel)
            Logger.info(msg)
            output.send(msg)


class Main(GridLayout):
    padding = [5, 5, 5, 5]
    spacing = [5, 5]

    def __init__(self, app, channel_name, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.config = app.config
        self.channel_name = channel_name
        self.render()

    def render(self):
        Logger.info('kimidi.main: rendering main, cleaning all widgets')
        self.clear_widgets()
        try:
            channel = int(self.config[f'channel {self.channel_name}']['number'])
        except ValueError:
            Logger.warning('kimidi.main: channel with name %s setted to number 0', self.channel_name)
            channel = 0
        for panel_name in settings._utils.purge_strings(
                self.config[f'channel {self.channel_name}']['panels'].split(',')):
            Logger.info('kimidi.main: adding panel %s in channel %s', panel_name, channel)
            self.add_widget(settings.panel.to_widget(
                self.config,
                panel_name,
                channel
            ))
        self.cols = 2
        self.rows = 1
        while len(self.children) > self.rows * self.cols:
            Logger.warning('kimidi.main: adding 1 row in Main')
            self.rows += 1


class KiMidiApp(App):
    settings = None
    sm = None
    cm = None

    def __init__(self, args=None, **kw):
        super().__init__(**kw)
        self.args = args

    def get_application_config(self):
        return super().get_application_config(
            f'%(appdir)s/{self.args.config_file}.ini'
        )

    def build(self):
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        self.sm = ScreenManager()
        self.cm = cm.CacheManager()
        self.cm.keys = self.parse_vkeybdmap()
        self.root = Root(self)
        return self.root

    def build_config(self, config):
        config.output = output
        settings.general.setdefaults(config)
        for name in settings.names_of.channels(config):
            settings.channel.setdefaults(config, name)
        for name in settings.names_of.panels(config):
            settings.panel.setdefaults(config, name)
        for name in settings.names_of.controllers(config):
            settings.control.setdefaults(config, name)

    def build_settings(self, _settings):
        self.settings = _settings  # so can be used on_config_change
        _settings.remove_widget(_settings.interface)  # resetting all settins panels widgets
        _settings.add_interface()  # reset all settings panels creating a new interface
        self.build_config(self.config)  # set defaults
        _settings.add_json_panel(
            'General',
            self.config,
            data=settings.general.dumps(),
        )
        for chan_name in settings.names_of.channels(self.config):
            _settings.add_json_panel(
                f'Channel {chan_name}',
                self.config,
                data=settings.channel.dumps(name=chan_name),
            )
        for panel_name in settings.names_of.panels(self.config):
            _settings.add_json_panel(
                f'Panel {panel_name}',
                self.config,
                data=settings.panel.dumps(name=panel_name),
            )
        _settings.add_json_panel(
            'Controls',
            self.config,
            data=settings.control.dumps(settings.names_of.panels(self.config), self.config)
        )

    def on_config_change(self, config, section, key, value):
        Logger.info('on_config_change: section="%s" key="%s" value=%s', section, key, value)
        rebuild = False
        if section == 'general' and key == 'channel_names':
            rebuild = True
        elif section.startswith('channel') and key == 'panels':
            rebuild = True
        elif section.startswith('panel') and key in ('panels', 'controls'):
            rebuild = True

        if rebuild:
            self.build_settings(self.settings)

        self.root.render()

    def parse_vkeybdmap(self):  # if you move this, change also __file__ below
        """If you wish you can share the same keyboard mapping of vkeyboard.
        This works even without vkeybd installed. but you should take care of locale"""
        available_keys = {}
        locations = [
            self.config.get('general', 'vkeybd_keymap_path'),
            '~/vkeybdmap',
            '/etc/vkeybdmap',
            '/usr/share/vkeybd/vkeybdmap',
            __file__.replace('main.py', '/vkeybdmap'),
        ]
        for _path in locations:
            try:
                with open(_path, 'r') as f:
                    content = f.read()
                    content = content[content.index('{') + 2:content.rindex('}') - 1]
                    for line in content.split('\n'):
                        c = line[line.index('{') + 1:line.rindex(' ')]
                        v = int(line[line.rindex(' ') + 1:line.index('}')])
                        available_keys[c] = v + self.cm.note_octave
                    return available_keys
            except FileNotFoundError:
                Logger.info('kimidi.app: %s not found', _path)
        raise Exception('no vkeybdmap file found!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', '-c', default='kimidi', help='config file (without .ini extension) that holds panels etc, defaults to kimidi')
    KiMidiApp(args=parser.parse_args()).run()
