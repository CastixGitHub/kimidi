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
def purge_strings(_list):
    """transform a iterable of strings, by stripping each string, removing empty ones, and removing duplicates,
    keeping the order. a list is retured"""
    return list(dict.fromkeys((e.strip() for e in _list if e.strip() != '')))


def split_purge(string, on=','):
    return purge_strings(string.split(on))
