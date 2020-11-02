import json
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, StringProperty, ListProperty
from mido import Message


Builder.load_string("""
<RadioButton>:
    on_touch_down: self.on_change_checkbox()
    GridLayout:
        cols: 2
        CheckBox:
            group: "checkbox"
            state: 'down'# if root.selected else 'normal'
            size: lab.height, lab.height
            pos: [0,0]
        Label:
            id: lab
            text: root.text
            markup: True
            size: [60, 20]
            pos: [0, 0]
""", filename="RadioButton.kv")


class RadioButton(ToggleButtonBehavior, BoxLayout):
    selected = BooleanProperty(False)
    text = StringProperty('RadioButton')
    color = StringProperty('ffffff')

    def __init__(self, name, channel, color, output, control, *a, **kw):
        super().__init__(*a, **kw)
        self.mido_output = output
        self.color = color.replace('#', '')
        self.text = f'[color={self.color}]{name}[/color]'
        self.channel = channel
        self.control = control

    # rewrite on_state Event handling method, when state Execute after value changes
    def on_state(self, widget, value):
        if value == 'down':
            # i should put {0: "sin"} instead...
            print(value, widget)
            self.selected = True
            msg = Message('control_change', control=self.control, channel=self.channel, value=0)
            self.mido_output.send(msg)

    # rewrite_do_press Method, when the radio container is clicked,
    # it is executed to solve the problem togglebutton Click again
    # after being selected to cancel the selected question
    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)
            self.selected = True

    def on_change_checkbox(self):
        ToggleButtonBehavior._do_press(self)
        self.selected = True


def midiselect(config, name, channel, color):
    try:
        values = json.loads(config[name]['values'])
    except json.decoder.JSONDecodeError:
        Logger.warning('kimidi.midiselect: values not valid json')
        values = []
    if len(values) < 4:
        inner = BoxLayout(orientation='vertical')
        for value in values:
            inner.add_widget(
                RadioButton(value, channel, color, config.output, int(config[name]['CC'])),
            )
        return inner
