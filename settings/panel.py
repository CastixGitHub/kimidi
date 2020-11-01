import json
from configparser import NoSectionError
from kivy.logger import Logger
from kivy.utils import get_color_from_hex
from settings import control
from settings._utils import purge_strings
from widgets.namedpanel import NamedPanel


def setdefaults(config, name):
    config.setdefaults(f'panel {name}', {
        'panels': '',
        'color': '#ffffff',
        'rows': 0,
        'cols': 0,
        'width': None,
        'controls': '',
    })


def to_widget(config, name, channel):
    # channel is just propagated to control.to_widget if it requires more config... refector to kwargs
    items = []
    try:
        for subpanel in purge_strings(config.get(f'panel {name}', 'panels').split(',')):
            items.append(to_widget(config, f'{name}.{subpanel}', channel))
    except NoSectionError:
        setdefaults(config, name)
    controls = purge_strings(config.get(f'panel {name}', 'controls').split(','))
    for c in controls:
        Logger.info('kimidi.settings.panel: adding control control.%s:%s', c, name)
        items.append(control.to_widget(config, f'control.{c}:{name}', channel))

    try:
        width = float(config.get(f'panel {name}', 'width')) / 100
        size_hint_x = None
    except ValueError:
        width = 1
        size_hint_x = 1
    cols = int(config.get(f'panel {name}', 'cols'))
    rows = int(config.get(f'panel {name}', 'rows'))
    np = NamedPanel(
        name,
        items=items,
        available_width=width,
        size_hint_x=size_hint_x,
        force_cols=cols,
        force_rows=rows,
    )
    np.border_color = get_color_from_hex(config.get(f'panel {name}', 'color'))
    np.name_color = get_color_from_hex(config.get(f'panel {name}', 'color'))
    return np


def dumps(name=None):
    if name is None:
        return []
    return json.dumps([
        {
            'key': 'color',
            'title': 'Color',
            'section': f'panel {name}',
            'type': 'string',
            'desc': '''rgb color like #ff00ee are well accepted.
Ask me if you wish to get a different color for text and border''',  # TODO: i18n
        },
        {
            'key': 'width',
            'title': 'Width',
            'section': f'panel {name}',
            'type': 'numeric',
            'desc': 'percentage of screen that this widget should have',  # TODO i18n
        },
        {
            'key': 'cols',
            'title': 'Columns Number',
            'section': f'panel {name}',
            'type': 'numeric',
            'desc': 'force number of column instead of autodetecting',
        },
        {
            'key': 'rows',
            'title': 'Rows Number',
            'section': f'panel {name}',
            'type': 'numeric',
            'desc': 'force number of rows instead of autodetecting',
        },
        {
            'key': 'panels',
            'title': 'Panels',
            'section': f'panel {name}',
            'type': 'string',
            'desc': 'comma separed, subpanels within this panel',  # TODO: i18n
        },
        {
            'key': 'controls',
            'title': 'Controls',
            'section': f'panel {name}',
            'type': 'string',
            'desc': 'knobs,sliders,etc',
        },
    ])
