from typing import Union, Any, Dict, Callable


Mapper = Union[Callable[[Any], Any], type]


def key_exists(value):
    return True


def pass_value(value):
    return value


class Converter:
    """
    Stores the properties of an object. It's a dictionary that's
    restricted to a tuple of allowed keys. Any attempt to set an invalid
    key raises an error. 

    args
    ----
    kwargs: Dict[str, [Union[Callable, type]]
        stores the callable which will be applied to the value of the respective keys during __call__

    
    the converter can be called on a dictionary, and checks that all keys are present, applies the 

    Example::
            
        convert = Converter(**{'x': str, 'y': int})
        convert = Converter(x=str, y=int)
        convert(**{"x":1, "y":"1")m
        convert(x=1, y="1")
        >> {'x': '1', 'y': 1}
    
    """

    def __init__(self, **kwargs: Mapper):
        # super(Converter, self).__init__(**kwargs)
        self.mapper: Dict[str, Mapper] = kwargs

    def __call__(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """call upon a dictionary to check key consistency and apply the callables to their respective key/values
        """
        other = dict()
        for key, convert in self.mapper.items():
            other[key] = convert(kwargs[key])
        return other

    def is_complete(self, other: Dict[str, str]) -> bool:
        o = set(k for k in other.keys())
        s = set(k for k in self.mapper.keys())
        if sorted(s) != sorted(o):
            return False
        else:
            return True


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
