# This file is part of KiMidi.

# KiMidi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# KiMidi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with KiMidi.  If not, see <https://www.gnu.org/licenses/>.
import json
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex, get_hex_from_color
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
    s.mido_output = App.get_running_app().cm.output
    s.channel = channel
    s.bind(value=_on_value)

    text = config[name]['text'] if config[name]['text'] != 'label' else name  # exclude default
    inner.add_widget(Label(
        text=f"[color={get_hex_from_color(color)}]{text}[/color]",
        size_hint=(1, 0.05),
        markup=True,
    ))
    inner.add_widget(s)
    return inner
