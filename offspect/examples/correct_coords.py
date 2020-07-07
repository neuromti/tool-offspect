from offspect.api import encode, decode, CacheFile
from offspect.types import TraceAttributes, TraceData, Coordinate
from typing import List, Union
import numpy as np


def rescale_coords(
    attrs: TraceAttributes, scaling_factor: float = 1.0
) -> TraceAttributes:
    """scale the coordinates of this trace by a scaling factor"""
    coords = decode(attrs["xyz_coords"])
    coords = [float * c for c in coords]
    attrs["xyz_coords"] = encode(coords)
    return attrs


def translate_coords(
    attrs: TraceAttributes, translation: List[float] = [0.0, 0.0, 0.0]
) -> TraceAttributes:
    """move the coordinates of this trace by a translation"""
    coords = decode(attrs["xyz_coords"])
    coords = [c - t for c, t in zip(coords, translation)]
    attrs["xyz_coords"] = encode(coords)
    return attrs


def calculate_translation(hotspots: Union[List[Coordinate], None] = None):
    """calculate the correction translation and scaling     
    args
    ----
    hotspots: List[List[float]]
        a list of the hotspot coordinates, one for each hemisphere. The correct hemisphere for each coordinate is determined automatically by its x coordinat. The order is therefore irrelevant. Each hotspot is a list of x, y, z coordinates. If this argument is left undefined or set to None (default), the function will calculate a translation to identity, i.e. one that will keep the coordinates unchanged.
    
    returns
    -------
    translation: List[List[float]]
        the translation for each hemisphere
        
    .. admonition:: Rationale
    
        For each hemisphere, we did usually perform a fast estimation of the hotspot. This hotspot was used as seed coordinate for a mapping. But it is not known whether the grid was centered on the hotspot, or in case it was, whether the mapping had to be aborted. Therefore, it can not be know for sure just by looking at all coordinates from a mapping, where the origin was. It is therefore necessary for the user to set the hotspot.

    """

    # M1 coordinates are based on Mayka, M. A., Corcos, D. M., Leurgans, S. E.
    # , & Vaillancourt, D. E. (2006): Three-dimensional locations and
    # boundaries of motor and premotor cortices as defined by functional brain
    # imaging: a meta-analysis. NeuroImage, 31(4), 14531474. https://doi.org/
    # 10.1016/j.neuroimage.2006.02.004
    # Consider that any MNI coordinates not reported in Talairach space were
    # converted using the transformation equations for above the AC line (z >
    # 0): xV = 0.9900x yV = 0.9688y + 0.0460z, zV = -0.0485y + 0.9189z
    # xyz_in_Tailarach    = [-37, -21, 58];
    # Tailarach2MNI       = [0.9900,0,0;0,0.9688,0.0460;0,-0.0485,0.9189];
    # xyz_in_MNI          = (Tailarach2MNI*xyz_in_Tailarach')';
    # Result as literals for speed
    # See also
    # https://neuroimage.usc.edu/brainstorm/CoordinateSystems
    # https://www.brainvoyager.com/bv/doc/UsersGuide/CoordsAndTransforms/
    # CoordinateSystems.html
    M1s = [[-36.6300, -17.6768, 54.3147], [36.6300, -17.6768, 54.3147]]

    # determine the hotspots, either from grid
    if hotspots is None:
        right = M1s[1]
        left = M1s[0]
    else:
        rights: List[List[float]] = []
        lefts: List[List[float]] = []
        for point in hotspots:
            if point[0] < 0:
                lefts.append(point)
            elif point[0] > 0:
                rights.append(point)
            else:
                raise ValueError(
                    f"Hotspot {point} lies on the vertex. Please select on with a clear lateralization"
                )
        if len(rights) > 1 or len(lefts) > 1:
            raise ValueError(
                "Please specify not more than two hotspots, and only one per hemisphere"
            )
        else:
            try:
                right = rights.pop()
            except IndexError:
                print("No right hotspot defined. Using default")
                right = M1s[1]
            try:
                left = lefts.pop()
            except IndexError:
                print("No left hotspot defined. Using default")
                left = M1s[0]

    translation_right = [np.round(r - m, 3) for r, m, in zip(right, M1s[1])]
    translation_left = [np.round(l - m, 3) for l, m, in zip(left, M1s[0])]
    translation = [translation_left, translation_right]
    return translation


if __name__ == "__main__":
    pass
