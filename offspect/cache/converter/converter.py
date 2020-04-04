from typing import Union, Any, Dict, Callable, List
from copy import deepcopy

Mapper = Union[Callable[[Any], Any], type]


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

    @classmethod
    def factory(cls, keys: List[str], foo: Callable):
        kwargs = dict()
        for key in keys:
            kwargs[key] = foo
        return cls(**kwargs)

    def __init__(self, **kwargs: Mapper):
        # super(Converter, self).__init__(**kwargs)
        self.mapper: Dict[str, Mapper] = kwargs

    def __call__(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """call upon a dictionary to check key consistency and apply the callables to their respective key/values
        """
        other = dict()
        for key, convert in self.mapper.items():
            try:
                value = kwargs[key]
            except KeyError:
                value = None  # type: ignore
            other[key] = convert(value)
        return other

    def keys(self):
        return list(self.mapper.keys())

    def is_complete(self, other: Dict[str, str]) -> bool:
        o = set(k for k in other.keys())
        s = set(k for k in self.mapper.keys())
        if sorted(s) != sorted(o):
            return False
        else:
            return True

    def __add__(self, other):
        copy = deepcopy(self)
        copy.mapper.update(**other.mapper)
        return copy

    def __repr__(self) -> str:
        d = dict()
        for k, v in self.mapper.items():
            d[k] = v.__name__
        return f"Converter(**{d})"
