from typing import List
from nibabel import Nifti1Image
from nilearn import plotting, image
import numpy as np
from itertools import chain
from numpy.linalg import pinv
import matplotlib.pyplot as plt
from functools import lru_cache
affine = np.asanyarray([[-1., 0., 0., 90.], [0., 1., 0., -126.],
                        [0., 0., 1., -72.], [0., 0., 0., 1.]])


@lru_cache(1)
def get_anatomical_mask() -> Nifti1Image:
    "get an anatomical mask based on MNI152"
    from nilearn.masking import compute_gray_matter_mask
    from nilearn.datasets import MNI152_FILE_PATH
    from  nilearn.image import resample_img
    mri = image.load_img(MNI152_FILE_PATH)
    mri = resample_img(mri, affine)
    anatomical_mask = compute_gray_matter_mask(mri)        
    return anatomical_mask


def mask_by_img(raw_img, mask_img=None) -> Nifti1Image:
    "mask an image using a masking image"
    if mask_img is None:
        mask_img = get_anatomical_mask()
    base = raw_img.get_fdata().copy()
    base *= mask_img.get_fdata()
    masked_img = Nifti1Image(base, affine)
    return masked_img

def get_M1(hemisphere="L", cosys="MNI") -> List:
    """
    According to Mayka, M. A., Corcos, D. M., Leurgans, S. E., & Vaillancourt, D. E. (2006):
    Three-dimensional locations and boundaries of motor and premotor cortices as defined by functional brain imaging: a meta-analysis. NeuroImage, 31(4), 14531474. https://doi.org/10.1016/j.neuroimage.2006.02.004
    Consider that any MNI coordinates not reported in Talairach space were converted using the transformation equations for above the AC line (z > 0):
    xV = 0.9900x yV = 0.9688y + 0.0460z, zV = -0.0485y + 0.9189z
    xyz_in_Tailarach    = [-37, -21, 58];
    Tailarach2MNI       = [0.9900,0,0;0,0.9688,0.0460;0,-0.0485,0.9189];
    xyz_in_MNI          = (Tailarach2MNI*xyz_in_Tailarach')';
    Result as literals for speed
    See also
    https://neuroimage.usc.edu/brainstorm/CoordinateSystems
    https://www.brainvoyager.com/bv/doc/UsersGuide/CoordsAndTransforms/CoordinateSystems.html
    """
    if cosys == "MNI":
        M1 = [-36.6300, -17.6768, 54.3147]
    elif cosys == "Tailarach":
        M1 = [-37, -21, 58]
    else:
        raise NotImplementedError("Unknown coordinate system")
    if hemisphere == "R":
        M1[0] = -M1[0]
        return M1
    elif hemisphere == "L":
        return M1
    else:
        raise NotImplementedError("Unknown hemisphere")


lM1 = get_M1("L")  #: has MNI coordinates (r-l, i.e. axis flipped)
rM1 = get_M1("R")  #: has MNI coordinates (r-l, i.e. axis flipped)


# ---------------------------------------------------------------------------
def project_into_nifti(coords:List[List[float]], 
                     values:List[float],
                     smooth:float=12.5) -> Nifti1Image:

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

    # mask by anatomy
    filled_img = mask_by_img(filled_img)
    return filled_img

def plot_glass(
        coords: List[List[float]],
        values: List[float],
        display_mode="z",  # lyrz 
        smooth: float = 12.5,
        colorbar:bool=True,
        vmax=None,
        title: str = ""):
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
    bmax = max(values)
    vmax = bmax if vmax is None else vmax    

    # plot the image
    fig = plt.figure(figsize=(6, 6), dpi=125)
    display = plotting.plot_glass_brain(filled_img,
                                        colorbar=colorbar,
                                        display_mode=display_mode,
                                        vmax=vmax,
                                        title=title,
                                        figure=fig)

    # scale and label colorbar
    if colorbar:
        ticks = display._cbar.get_ticks()
        display._cbar.set_ticklabels([f"{t:3.0f}µV" for t in ticks])
    #display.add_contours(filled_img, filled=True, levels=[0], colors='r')
    display.show = plotting.show
    return display


def plot_m1s(coords = [lM1, rM1], values = [200., 200.]):
    "plots the left and right M1 on a glass-brain"
    display = plot_glass(coords, values, title="M1s")
    return display
