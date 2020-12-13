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
