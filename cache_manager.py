# pylint: disable=no-self-use
from kivy.cache import Cache
from kivy.logger import Logger
from mido import open_output
import modes


# use cache only for temporary stuff you don't wish to save
class CacheManager:
    def __init__(self):
        Cache.register('kimidi', timeout=None)
        Cache.append('kimidi', 'mido_output', open_output())

    @property
    def major_mode(self):
        name = Cache.get('kimidi', 'major_mode', 'fundamental')
        try:
            return getattr(modes, name)
        except AttributeError:
            Logger.error('kimidi.cache_manager: add mode {name} in modes/__init__.py')
            return getattr(modes, 'fundamental')

    @major_mode.setter
    def major_mode(self, name):
        Cache.append('kimidi', 'major_mode', name)

    @property
    def minor_modes_names(self):
        return Cache.get('kimidi', 'minor_modes', [])

    @minor_modes_names.setter
    def minor_modes_names(self, names):
        Cache.append('kimidi', 'minor_modes', names)

    @property
    def minor_modes(self):
        return [getattr(modes, name) for name in self.minor_modes_names]

    def toggle_minor_mode(self, name, force=None):
        names = self.minor_modes_names
        was_there = name in names
        if not was_there or force == 1:
            names.append(name)
        if was_there or force == 0:
            names.remove(name)
        self.minor_modes_names = list(set(names))
        return name in self.minor_modes_names

    @property
    def output(self):
        return Cache.get('kimidi', 'mido_output')

    @property
    def channel(self):
        return Cache.get('kimidi', 'channel', 0)

    @channel.setter
    def channel(self, chan):
        Cache.append('kimidi', 'channel', chan)

    @property
    def keys(self):
        return Cache.get('kimidi', 'available_keys', {})

    @keys.setter
    def keys(self, dict_):
        Cache.append('kimidi', 'available_keys', dict_)

    @property
    def note_octave(self):
        return Cache.get('kimidi', 'note_octave', 6 * 8)

    @note_octave.setter
    def note_octave(self, octave):
        old = Cache.get('kimidi', 'note_octave', 6 * 8)
        new = 8 * octave
        Cache.append('kimidi', 'note_octave', new)
        keys = self.keys
        for k, v in keys.items():
            keys[k] = v - old + new
        self.keys = keys

    @property
    def active_notes(self):  # should be separated by channel?
        return Cache.get('kimidi', 'active_notes', [])

    def activate_note(self, note):
        """Returns False if the note was already active"""
        notes = self.active_notes
        if note not in notes:
            notes.append(note)
            Cache.append('kimidi', 'active_notes', notes)
            return True
        return False

    def release_note(self, note):
        """Returns True if the note was active"""
        notes = self.active_notes
        if note in notes:
            Cache.append('kimidi', 'active_notes', [n for n in notes if n != note])
            return True
        return False
