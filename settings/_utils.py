def purge_strings(_list):
    return sorted({e.strip() for e in _list if e.strip() != ''})
