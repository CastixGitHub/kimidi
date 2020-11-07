import json
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from kivy.logger import Logger
from mido import Message


def _on_value(obj, value):
    msg = Message('control_change', value=int(value), control=obj.control, channel=obj.channel)
    obj.mido_output.send(msg)
    Logger.info(msg)


def midislider(config, name, channel, color):
    inner = BoxLayout(orientation='vertical')
    try:
        minimum = int(json.loads(config[name]['values']).get('min', '0'))
        maximum = int(json.loads(config[name]['values']).get('max', '0'))
    except json.decoder.JSONDecodeError:
        minimum = 0
        maximum = 127

    color = get_color_from_hex(config[name]['color'])

    s = Slider(
        range=(minimum, maximum),
        value=config[name].get('default', 100),
        value_track=True,
        value_track_color=color,
        value_track_width=4,
        orientation='vertical',
        background_width=0,
        padding=25,
        cursor_size=[0, 0],
        size_hint=(1, 0.95),
    )
    s.control = int(config[name]['CC'])
    s.mido_output = config.output
    s.channel = channel
    s.bind(value=_on_value)

    text = config[name]['text'] if config[name]['text'] != 'label' else name  # exclude default
    print(color, text)
    inner.add_widget(Label(
        text=f"[color={color}]{text}[/color]",
        size_hint=(1, 0.05),
        markup=True,
        text_size=(60, 20),
        
    ))
    inner.add_widget(s)
    return inner
