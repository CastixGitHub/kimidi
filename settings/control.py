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
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from settings._utils import purge_strings
from widgets.midiknob import MidiKnob
from widgets.midislider import midislider
from widgets.midiselect import midiselect


def to_widget(config, name, channel):
    panel_name = 'panel ' + name.split(':')[1]
    parent_color = config[panel_name]['color']
    # do not search upper lever parents beacuse all panels have a color, if the upper is default white,
    # these controls will be white too. keeping as a comment for now, as an example maybe...
    # an orrible example
    # while '.' in panel_name:  # search for the parent color backwardly in panels hierarchy
    #     panel_name = '.'.join(panel_name.split('.')[:-1])
    #     if not parent_color:
    #         parent_color = config[panel_name]['color']
    try:
        color = config[name]['color'] or parent_color
    except KeyError:
        Logger.exception('kimidi.settings.control: no %s configured', name)
        color = parent_color
        setdefaults(config, name)

    text = config[name]['text']
    if text == 'label':  # skip the default one, getting it from the panel
        text = name.split(':')[0].split('.')[1]

    if config[name]['kind'] == 'knob':
        try:
            minimum = int(json.loads(config[name]['values']).get('min', '0'))
            maximum = int(json.loads(config[name]['values']).get('max', '0'))
        except json.decoder.JSONDecodeError:
            minimum = 0
            maximum = 127
        inner = BoxLayout(orientation='horizontal')
        inner.add_widget(MidiKnob(
            text,
            channel,
            control=int(config[name]['CC']),
            color=color,
            minimum=minimum,
            maximum=maximum,
        ))
        return inner
    if config[name]['kind'] == 'slider':
        return midislider(config, name, channel, color)
    if config[name]['kind'] == 'select':
        return midiselect(config, name, channel, color)


def setdefaults(config, name):
    config.setdefaults(name, {
        'cc': 1,
        'text': 'label',
        'color': '',
        'kind': 'knob',
        'values': '{"min": 0, "max": 127}',
        'help': '',
    })


def dumps(panel_names, config):
    controllers = []
    for panel_name in panel_names:
        controllers_names = purge_strings(config.get(f'panel {panel_name}', 'controls').split(','))
        for cn in controllers_names:
            # TODO: fix useless json encoding/decoding
            controllers.extend(json.loads(dumps_single(panel_name, cn, f'{panel_name} - {cn} - ')))
        if len(controllers_names):
            controllers.extend([
                {
                    'key': 'empty',
                    'title': '',
                    'section': 'general',
                    'type': 'string',
                    'desc': '',  # used just as a separator
                },
            ])
    return json.dumps(controllers)


def dumps_single(panel, name, titles_prefix=''):
    section = f'control.{name}:{panel}'
    controller = [
        {
            'key': 'cc',
            'title': f'{titles_prefix}CC',
            'section': section,
            'type': 'numeric',
            'desc': 'from 0 to 127 MIDI Control Change to be sent',
        },
        {
            'key': 'text',
            'title': f'{titles_prefix}Text',
            'section': section,
            'type': 'string',
            'desc': 'short label that will appear above the widget,'
                    ' if is "label" will use the id used in the panel that generated this',
        },
        {
            'key': 'color',
            'title': f'{titles_prefix}Color',
            'section': section,
            'type': 'string',
            'desc': 'rgb color like #ff00ee are well accepted',  # TODO: i18n
        },
        {
            'key': 'kind',
            'title': f'{titles_prefix}Kind',
            'section': section,
            'type': 'options',
            'options': ['knob', 'slider', 'select', 'button'],
            'desc': 'kind of control',  # TODO: i18n
        },
        {
            'key': 'values',
            'title': f'{titles_prefix}Values',
            'section': section,
            'type': 'string',
            'desc': '{"min": 0, "max": 127} for knob or {"sin": 0, "cos": 1, "tri": 2} for select (json format)',
        },
        {
            'key': 'help',
            'title': f'{titles_prefix}Help',
            'section': section,
            'type': 'string',
            'desc': 'tooltip that will appear when you forget what does this CC',  # TODO: i18n
        },
    ]
    return json.dumps(controller)
