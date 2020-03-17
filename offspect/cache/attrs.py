from typing import Union, Any, Dict
from offspect.cache.check import *


class Converter(dict):
    """
    Stores the properties of an object. It's a dictionary that's
    restricted to a tuple of allowed keys. Any attempt to set an invalid
    key raises an error.
    """

    def __init__(self, **kwargs):
        """
        Initializes the class instance. The allowed_keys tuple is
        required, and it cannot be changed later.
        If seq and/or kwargs are provided, the values are added (just
        like a normal dictionary).

        Example::
            
            Encoder(**{'x': str, 'y': int})
            Encoder(x=str, y=int)

        """
        super(Converter, self).__init__()
        self._allowed_keys = tuple(kwargs.keys())
        # normalize arguments to a (key, value) iterable
        # scan the items keeping track of the keys' order
        for k, v in kwargs.items():
            if not type(v) == type or type(v) == callable:
                raise ValueError(f"{v} is not a valid converter")
            self.__setitem__(k, v)

    def __setitem__(self, key, value):
        """Checks if the key is allowed before setting the value"""
        if key in self._allowed_keys:
            super(Converter, self).__setitem__(key, value)
        else:
            raise KeyError("%s is not allowed" % key)

    def __getitem__(self, key):
        """Checks if the key is allowed before setting the value"""
        if key in self._allowed_keys:
            return super(Converter, self).__getitem__(key)
        else:
            raise KeyError("%s is not allowed" % key)

    def update(self, e=None, **kwargs):
        """
        Equivalent to dict.update(), but it was needed to call
        Converter.__setitem__() instead of dict.__setitem__
        """
        try:
            for k in e:
                self.__setitem__(k, e[k])
        except AttributeError:
            for (k, v) in e:
                self.__setitem__(k, v)
        for k in kwargs:
            self.__setitem__(k, kwargs[k])

    def __call__(self, **kwargs):
        d = dict()
        for k, v in kwargs.items():
            d[k] = self[k](v)
        return d

    def is_complete(self, other: Dict[str, str]) -> bool:
        o = set(k for k in other.keys())
        s = set(k for k in self.keys())
        if sorted(s) != sorted(o):
            return False
        else:
            return True
# -----------------------------------------------------------------------------


def _coords(item: str) -> str:
    if iscoords(item):
        return str(item)
    else:
        raise ValueError(f"{item} is not a valid coordinate")


# -----------------------------------------------------------------------------
OriginEncoder = Converter(
    **{
        "channel_labels": list,
        "samples_post_event": int,
        "samples_pre_event": int,
        "samplingrate": int,
        "subject": str,
        "readout": str,
        "comment": str,
        "filedate": str,
        "history": str,
        "version": str,
    }
)

OriginDecoder = Converter(
    **{
        "channel_labels": str,
        "samples_post_event": str,
        "samples_pre_event": str,
        "samplingrate": str,
        "subject": str,
        "readout": str,
        "comment": str,
        "filedate": str,
        "history": str,
        "version": str,
    }
)
