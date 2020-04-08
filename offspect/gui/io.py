from offspect.api import encode, CacheFile, decode
from typing import Callable


def save_global(cf, idx: int, key: str, read: Callable):
    tattr = cf.get_trace_attrs(idx)
    text = read()
    if tattr[key] == text:
        return
    else:
        origin = tattr["origin"]
        for idx in range(len(cf)):
            tattr = cf.get_trace_attrs(idx)
            if tattr["origin"] == origin:
                tattr[key] = encode(text)
                cf.set_trace_attrs(idx, tattr)
        print(f"CF: Wrote globaly {origin}: {key} {text}")


def save(cf, idx: int, key: str, read: Callable):
    tattr = cf.get_trace_attrs(idx)
    text = read()
    if tattr[key] == text:
        return
    else:
        tattr[key] = encode(text)
        cf.set_trace_attrs(idx, tattr)
        print(f"CF: Wrote {idx}: {key} {text}")
