from numpy import ndarray
from typing import Union, List, Dict, Any, Tuple
from pathlib import Path

TraceData = ndarray  #: A trace, i.e. an array of samples for one or more channels stored in a cachefile


FileName = Union[str, Path]  #: The name of a file in the operating system

MetaValue = Union[
    str, int, float, List[str]
]  #: a specific  metadata attribute. Must be one of these types

MetaData = Dict[str, MetaValue]  #: A specific metadata element from an HDF5 cachefile

Annotations = Dict[
    str, Any
]  #: A dictionary with fields origin, origin attributes and trace attributes, the latter being a List of MetaData for each specific Trace

TraceAttributes = Dict[
    str, MetaValue
]  #:  Collapsed annotations with information on origin, origin attributes and a specific trace all in one Dictionary

Coordinate = Tuple[float, float, float]

Coords = Dict[int, Coordinate]

