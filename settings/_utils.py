def purge_strings(_list):
    """transform a iterable of strings, by stripping each string, removing empty ones, and removing duplicates,
    keeping the order. a list is retured"""
    return list(dict.fromkeys((e.strip() for e in _list if e.strip() != '')))


def split_purge(string, on=','):
    return purge_strings(string.split(on))
