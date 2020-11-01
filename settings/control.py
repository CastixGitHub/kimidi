import json
from kivy.uix.boxlayout import BoxLayout
from settings._utils import purge_strings
from widgets.midiknob import MidiKnob
from widgets.midislider import midislider


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

    if config[name]['kind'] == 'knob':
        inner = BoxLayout(orientation='horizontal')
        inner.add_widget(MidiKnob(
            config.output,
            config[name]['text'],
            channel,
            control=int(config[name]['CC']),
            color=config[name]['color'] or parent_color,
        ))
        return inner
    elif config[name]['kind'] == 'slider':
        return midislider(config, name, channel, config[name]['color'] or parent_color)


def setdefaults(config, name):
    config.setdefaults(name, {
        'cc': 1,
        'text': 'label',
        'color': '',
        'kind': 'knob',
        'minimum': 0,
        'maximum': 127,
        'help': ''
    })


def dumps(panel_names, config):
    controllers = []
    for panel_name in panel_names:
        controllers_names = purge_strings(config.get(f'panel {panel_name}', 'controls').split(','))
        for cn in controllers_names:
            section = f'control.{cn}:{panel_name}'
            controllers.extend([
                {
                    'key': 'cc',
                    'title': f'{panel_name} - {cn} - CC',
                    'section': section,
                    'type': 'numeric',
                    'desc': 'from 0 to 127 MIDI Control Change to be sent',
                },
                {
                    'key': 'text',
                    'title': f'{panel_name} - {cn} - Text',
                    'section': section,
                    'type': 'string',
                    'desc': 'short label that will appear within the widget',
                },
                {
                    'key': 'color',
                    'title': f'{panel_name} - {cn} - Color',
                    'section': section,
                    'type': 'string',
                    'desc': 'rgb color like #ff00ee are well accepted',  # TODO: i18n
                },
                {
                    'key': 'kind',
                    'title': f'{panel_name} - {cn} - Kind',
                    'section': section,
                    'type': 'options',
                    'options': ['knob', 'slider', 'select', 'button'],
                    'desc': 'kind of control',  # TODO: i18n
                },
                {
                    'key': 'minimum',
                    'title': f'{panel_name} - {cn} - Min',
                    'section': section,
                    'type': 'numeric',
                    'desc': 'minimum value available',  # TODO: i18n
                },
                {
                    'key': 'maximum',
                    'title': f'{panel_name} - {cn} - Max',
                    'section': section,
                    'type': 'numeric',
                    'desc': 'maximum value available',  # TODO: i18n
                },
                {
                    'key': 'help',
                    'title': f'{panel_name} - {cn} - Help',
                    'section': section,
                    'type': 'string',
                    'desc': 'tooltip that will appear when you forget what does this CC',  # TODO: i18n
                },
            ])
        if len(controllers_names):
            controllers.extend([
                {
                    'key': 'empty',
                    'title': '',
                    'section': 'general',
                    'type': 'string',
                    'desc': '',  # used jest as a separator
                },
            ])
    return json.dumps(controllers)
