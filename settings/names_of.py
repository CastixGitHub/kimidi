from configparser import NoSectionError
from settings._utils import purge_strings, split_purge
import settings


def channels(config):
    return sorted(
        split_purge(config.get('general', 'channel_names')),
        key=lambda n: config.get(f'channel {n}', 'number'),
    )


def panels(config):
    names = []
    for chan_name in channels(config):
        names.extend(split_purge(config.get(f'channel {chan_name}', 'panels')))
    for name in names:
        try:
            names.extend([
                f'{name}.{subp}' for subp in
                split_purge(config.get(f'panel {name}', 'panels'))
            ])
        except NoSectionError:
            settings.panel.setdefaults(config, name)
    return purge_strings(names)


def controllers(config):
    names = []
    for panel_name in panels(config):
        for cn in split_purge(config.get(f'panel {panel_name}', 'controls')):
            names.extend([f'control.{cn}:{panel_name}'])
    return names
