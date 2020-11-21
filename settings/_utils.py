def purge_strings(_list):
    return list({e.strip() for e in _list if e.strip() != ''})


def split_purge(string, on=','):
    return purge_strings(string.split(on))
