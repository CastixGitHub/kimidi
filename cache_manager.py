from kivy.cache import Cache


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# use cache only for temporary stuff you don't wish to save
class CacheManager(metaclass=Singleton):
    def __init__(self):
        Cache.register('kimidi', timeout=None)

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
