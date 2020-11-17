"""KiMidi application entry point"""
# pylint: disable=wrong-import-position
import os
import argparse
os.environ["KIVY_NO_ARGS"] = "1"
from kivy.lang import Builder  # noqa: E402
from kivy.logger import Logger  # noqa: E402
from kivy.app import App  # noqa: E402
from kivy.uix.settings import SettingsWithSidebar  # noqa: E402
from kivy.uix.gridlayout import GridLayout  # noqa: E402
from kivy.uix.floatlayout import FloatLayout  # noqa: E402
from kivy.uix.screenmanager import ScreenManager, Screen  # noqa: E402
from kivy.uix.button import Button  # noqa: E402
import settings  # noqa: E402
from modes import KeyboardAdapter  # noqa: E402
import cache_manager as cm  # noqa: E402


class Root(FloatLayout, KeyboardAdapter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.add_widget(self.app.sm)
        self.app.cm.note_octave = int(self.app.config.get('general', 'base_octave'))
        self.render()

    def init_screens(self):
        # also setup the keyboard, as can be closed by the settings
        self.setup_keyboard()
        
        current = self.app.sm.current
        self.app.sm.clear_widgets()
        for channel_name in settings.names_of.channels(self.app.config):
            Logger.info('kimidi.root: adding channel %s', channel_name)
            screen = Screen(name=channel_name)
            screen.add_widget(Main(channel_name))  # kwargs should be passed
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


class Main(GridLayout):
    padding = [5, 5, 5, 5]
    spacing = [5, 5]

    def __init__(self, channel_name, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.config = self.app.config
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

    def get_application_config(self, _defaultpath=None):
        return super().get_application_config(
            f'%(appdir)s/{self.args.config_file}.ini'
        )

    def build(self):
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        self.sm = ScreenManager()
        self.cm = cm.CacheManager()
        self.cm.keys = self.parse_vkeybdmap()
        self.root = Root()
        return self.root

    def build_config(self, config):
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
            'Controls (do not use this, use edit mode instead (C-e and click a control))',
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

        if section == 'general' and key == 'base_octave':
            self.cm.note_octave = int(value)

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
    parser.add_argument(
        '--config-file',
        '-c',
        default='kimidi',
        help='config file (without .ini extension) that holds panels etc, defaults to kimidi',
    )

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

    KiMidiApp(args=parser.parse_args()).run()
