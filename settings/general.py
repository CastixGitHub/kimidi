import json

from settings._utils import split_purge


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


def on_config_change(config, section, key, value):
    if section == 'general':
        if key == 'channel_names':
            old = split_purge(config.get('general', 'channel_names'))
            old_channels = [config[f'channel {ch}'] for ch in old]
            new = split_purge(value)
            new_channels = [config[f'channel {ch}'] for ch in split_purge(new)]
            if len(old_channels) == len(new_channels):
                pass
