from kivy.lang import Builder
from kivy.logger import Logger
from kivy.app import App
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from mido import open_output

import settings

output = open_output()


Builder.load_string("""
<Root>:
    Button:
        text: 'settings'
        font_size: 20
        pos: [root.width - self.width - 10, root.height - self.height - 10]
        size_hint: [.05, .05]
        on_release: app.open_settings()
""", filename='Root.kv')


class Root(FloatLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        for channel_name in settings.names_of.channels(app.config):
            Logger.info('kimidi.root: adding channel %s', channel_name)
            screen = Screen(name=channel_name)
            screen.add_widget(Main(app, channel_name, **kwargs))
            self.app.sm.add_widget(screen)

        self.add_widget(self.app.sm)
        self.render()

    def render(self):
        # assuming there is only main widget inside a screen
        main = self.app.sm.current_screen.children[0]
        main.channel_name = self.app.sm.current
        main.render()


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

    def build(self):
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        self.sm = ScreenManager()
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


if __name__ == '__main__':
    KiMidiApp().run()
