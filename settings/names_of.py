from configparser import NoSectionError
from settings._utils import purge_strings
import settings


def channels(config):
    names = config.get('general', 'channel_names').split(',')
    return purge_strings(names)


def panels(config):
    names = []
    for chan_name in channels(config):
        names.extend(purge_strings(config.get(f'channel {chan_name}', 'panels').split(',')))
    for name in names:
        try:
            names.extend([
                f'{name}.{subp}' for subp in
                purge_strings(config.get(f'panel {name}', 'panels').split(','))
            ])
        except NoSectionError:
            settings.panel.setdefaults(config, name)
    return purge_strings(names)


def controllers(config):
    names = []
    for panel_name in panels(config):
        for cn in purge_strings(config.get(f'panel {panel_name}', 'controls').split(',')):
            names.extend([f'control.{cn}:{panel_name}'])
    return names

