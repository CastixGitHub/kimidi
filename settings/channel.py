import json


def setdefaults(config, name):
    config.setdefaults(f'channel {name}', {
        'number': '',
        'panels': '',
        'rows': 1,
        'cols': 1,
    })


def dumps(name=None, panels=None):
    if name is None:
        return []
    if panels is None:
        panels = []
    return json.dumps([
        {
            'key': 'number',
            'title': 'Number',
            'section': f'channel {name}',
            'type': 'numeric',
            'desc': 'number of the channel',  # TODO: i18n
        },
        {
            'key': 'rows',
            'title': 'Rows',
            'section': f'channel {name}',
            'type': 'numeric',
            'desc': 'force number of columns, by default is the number of panels',
        },
        {
            'key': 'cols',
            'title': 'Cols',
            'section': f'channel {name}',
            'type': 'numeric',
            'desc': 'force number of rows, by default 1',
        },
        {
            'key': 'panels',
            'title': 'Panels',
            'section': f'channel {name}',
            'type': 'string',
            'desc': 'panels that are in this channel',  # TODO: i18n
        },
    ])
