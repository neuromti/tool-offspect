from typing import List
from nibabel import Nifti1Image
from nilearn import plotting, image
import numpy as np
from itertools import chain
from numpy.linalg import pinv
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
def project_into_nifti(
    coords: List[List[float]], values: List[float], smooth: float = 12.5
) -> Nifti1Image:

    """takes a list of coordinates and values and projects them as a NiftiImage
    args
    ----
    coords:
        a list of [x,y,z] coordinates in MNI space
    values:
        a list of values for each coordinate
    smooth:float
        how much the points should be smoothened during projection
    returns: Nifti1Image
        the coords/values projected into a Nifti1Image
    
    Because after smoothening, values are decreased, the resulting image is rescaled to the original maximum value as given in the raw data.
    """
    affine = np.asanyarray(
        [
            [-1.0, 0.0, 0.0, 90.0],
            [0.0, 1.0, 0.0, -126.0],
            [0.0, 0.0, 1.0, -72.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    shape = (181, 217, 181)
    base = np.zeros(shape)
    for pos, val in zip(coords, values):
        apos = pinv(affine).dot(list(chain(pos, [1])))
        x, y, z, s = (int(p) for p in apos)
        try:
            base[x, y, z] = val
        except IndexError:
            pass

    filled_img = Nifti1Image(base, affine)
    filled_img = image.smooth_img(filled_img, smooth)

    # scale the data
    #
    # get the maximum of the smoothened data
    emax = filled_img.get_fdata().max()
    # get the maximum of the original data
    bmax = max(values)
    # rescale accordingly
    filled_img._dataobj /= emax
    filled_img._dataobj *= bmax
    return filled_img


def plot_glass(
    coords: List[List[float]],
    values: List[float],
    display_mode="z",  # lyrz
    smooth: float = 12.5,
    colorbar: bool = True,
    vmax=None,
    title: str = "",
):
    """takes a list of coordinates and values and plots them as glass-brain
    args
    ----
    coords:
        a list of [x,y,z] coordinates in MNI space
    values:
        a list of values for each coordinate
    display_mode:
        which views to plot, defaults to 'z', i.e. top-down view
    smooth:float
        how much the points should be smoothened during projection
    colorbar:
        whether to plot a colorbar or not, defaults to plotting one    
    vmax:
        the maximum value for scaling the colorbar. Defaults to adapting it to the data at hand
    title:
        a textual annotation to print into the upper left corner
    returns
    -------
    display:
        the glass-plot object
    """
    # project coordinages and values into a Nifti-Image
    filled_img = project_into_nifti(coords, values, smooth)

    # select the maximum of the colorbar
    # - either based on the data or the argument

    # plot the image
    fig = plt.figure(figsize=(6, 6), dpi=125)
    display = plotting.plot_glass_brain(
        filled_img,
        colorbar=colorbar,
        display_mode=display_mode,
        vmax=vmax,
        title=title,
        figure=fig,
    )

    # scale and label colorbar
    if colorbar:
        ticks = display._cbar.get_ticks()
        display._cbar.set_ticklabels([f"{t:3.0f}µV" for t in ticks])
    # display.add_contours(filled_img, filled=True, levels=[0], colors='r')
    display.show = plotting.show
    return display
