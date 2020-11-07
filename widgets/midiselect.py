import json
from uuid import uuid4
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from mido import Message


Builder.load_string("""
<RadioButton@StackLayout>:
    CheckBox:
        id: check
        group: root.uuid
        size_hint_x: None
        width: 30
        height: 15
    Label:
        id: lab
        text: root.text
        markup: True
        size_hint_x: None
        text_size: 60, 15
        width: 60
        shorten: True
        shorten_from: 'right'
        halign: 'left'
""", filename="RadioButton.kv")


class RadioButton(ToggleButtonBehavior, StackLayout):
    selected = BooleanProperty(False)
    text = StringProperty('RadioButton')
    color = StringProperty('ffffff')
    uuid = StringProperty()
    value = NumericProperty()

    def __init__(self, value, channel, color, output, control, *a, **kw):
        self.uuid = kw.pop('uuid')
        super().__init__(*a, **kw)
        self.mido_output = output
        self.color = color.replace('#', '')
        self.value = value[1]
        self.text = f'[color={self.color}]{value[0]}[/color]'
        self.channel = channel
        self.control = control

        def on_active(checkbox, value):
            if value:
                msg = Message('control_change', control=self.control, channel=self.channel, value=self.value)
                print(msg)
                self.mido_output.send(msg)
        self.ids['check'].bind(active=on_active)


Builder.load_string("""
<RadioButtonGroup@BoxLayout>:
    orientation: 'vertical'
    Label:
        text: root.text
        markup: True
        text_size: 60, 20
        #size_hint: 0.9, None
        #pos: 0, 0
        halign: 'left'
""", filename="RadioButtonGroup.kv")


class RadioButtonGroup(BoxLayout):
    text = StringProperty('radiogroup')
    def __init__(self, text, values, channel, color, output, cc, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        uuid = str(uuid4())
        for value in values.items():
            self.add_widget(
                RadioButton(value, channel, color, output, cc, uuid=uuid),
            )


def midiselect(config, name, channel, color):
    try:
        values = json.loads(config[name]['values'])
    except json.decoder.JSONDecodeError:
        Logger.exception('kimidi.midiselect: values not valid json')
        values = []
    if len(values) < 4:
        return RadioButtonGroup(
            name.split(':')[0].split('.')[1],
            values,
            channel,
            color,
            config.output,
            int(config[name]['CC']),
        )
