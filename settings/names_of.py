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
from configparser import NoSectionError
from settings._utils import purge_strings, split_purge
import settings


def channels(config):
    return split_purge(config.get('general', 'channel_names'))


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
