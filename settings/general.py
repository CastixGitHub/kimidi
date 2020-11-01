import json


def setdefaults(config):
    config.setdefaults('general', {
        'channel_names': '',
        'base_octave': 6,
        'vkeybd_keymap_path': '~/.vkeybdmap',
        'empty': '',
    })


def dumps():
    return json.dumps([
        {
            'key': 'channel_names',
            'title': 'Channels',
            'section': 'general',
            'type': 'string',
            'desc': 'comma separed names of the available channels',  # TODO: i18n
        },
        {
            'key': 'base_octave',
            'title': 'Base Octave',
            'section': 'general',
            'type': 'numeric',
            'desc': 'note multiplier for the keyboard',  # TODO: i18n
        },
        {
            'key': 'vkeybd_keymap_path',
            'title': 'vkeybd keymap path',
            'section': 'general',
            'type': 'path',
            'desc': 'optional, in this file you can specify which notes are played by your keyboard',
        },
    ])
