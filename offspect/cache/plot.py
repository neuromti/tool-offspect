from typing import List
from nibabel import Nifti1Image
from nilearn import plotting, image
import numpy as np
from itertools import chain
from numpy.core.numeric import NaN
from numpy.linalg import pinv
import matplotlib.pyplot as plt
from offspect.cache.attrs import decode
from math import nan
import matplotlib
from tempfile import TemporaryDirectory
from pathlib import Path
from functools import lru_cache
from offspect.cache.file import CacheFile
from collections import Counter


def plot_trace(ax, data, attrs):

    pre = decode(attrs["samples_pre_event"])
    post = decode(attrs["samples_post_event"])
    fs = decode(attrs["samplingrate"])
    t0 = -float(pre) / float(fs)
    t1 = float(post) / float(fs)

    # plot data
    ax.plot([pre, pre], [-200, 200], ":r")
    ax.plot(data)
    ax.set_ylim(-200, 200)
    ax.grid(True, which="both")
    ax.set_xticks((0, pre, pre + post))
    ax.set_xticklabels((t0, 0, t1))
    ax.set_xticks(range(0, pre + post, (pre + post) // 10), minor=True)
    ax.tick_params(direction="in")


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
    reps = np.zeros(shape)
    out_of_scope = 0.0
    for pos, val in zip(coords, values):
        apos = pinv(affine).dot(list(chain(pos, [1])))
        try:
            x, y, z, s = (int(p) for p in apos)
            base[x, y, z] += val
            reps[x, y, z] += 1

        except IndexError:
            out_of_scope += 1
            continue
    # print("Valid", pos, "->", x, y, z, val)

    if out_of_scope > 0:
        print(
            f"{out_of_scope:3.0f} values were ignored because their coords are outside of the plot"
        )

    reps[reps == 0] = 1
    averaged = base / reps

    unto: dict = Counter(reps.flatten())
    del unto[1.0]
    for k, v in sorted(unto.items(), reverse=True):
        print(f"{v:3.0f} times, {k:0.0f} values were projected on a single voxel.")

    filled_img = Nifti1Image(base, affine)
    filled_img = image.smooth_img(filled_img, smooth)

    # scale the data
    #
    # get the maximum of the smoothened data
    emax = filled_img.get_fdata().max()
    # get the maximum of the original data
    bmax = averaged.max()

    if emax == 0 or bmax == 0:
        print("All usable values were zero")
        return filled_img
    else:
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
    # the resolution sets the intercept and slope used for easy 2D plotting of
    # coordinates
    # for figsize=(5, 5), dpi=100 these are roughly the
    # origin at (247, 207) and each mm step is 2.6 pixels away
    #
    # from scipy.stats import linregress
    #
    # x = [-50, 0, 10, 20, 50]
    # y = [166, 247, 273, 299, 377]
    # slope, intercept, *_ = linregress(x, y)
    # print(f"{intercept} + {slope} * x")

    # x = [-40, 0, 10, 40]
    # y = [314, 207, 181, 103]
    # slope, intercept, *_ = linregress(x, y)
    # print(f"{intercept} + {slope} * y")

    fig = plt.figure(figsize=(5, 5), dpi=100)
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
        if not hasattr(display, "_cbar"):
            print("Invalid cbar likely because all values are zero")
        else:
            ticks = display._cbar.get_ticks()
            display._cbar.set_ticklabels([f"{t:3.0f}µV" for t in ticks])
    # display.add_contours(filled_img, filled=True, levels=[0], colors='r')
    display.show = plotting.show
    return display


def plot_glass_on_old(axes, coords, values):
    print("Deprecated, please use plot_glass instead")
    if "nan" in coords:
        return

    bg = plot_glass(
        coords,
        values=values,
        display_mode="z",
        smooth=12.5,
        colorbar=False,
        vmax=None,
        title="",
    )
    with TemporaryDirectory() as folder:
        fname = Path(folder) / "background.png"
        print(f"Saved  temporary figure to {fname}")
        bg.savefig(fname)
        bg.close()
        im = matplotlib.pyplot.imread(str(fname))
        print(f"Loaded temporary figure from {fname}")

    axes.imshow(im)


def plot_glass_on(axes, coords, tmpdir, width=10):

    if type(coords) != list:
        raise Exception(
            f"COORDS:xyz_coordinates {coords} are invalid, as they are not a list of floats"
        )
    for pos in coords:
        if pos == NaN or pos == nan:
            print("pos is nan")
        if type(pos) not in [int, float]:
            raise Exception(
                f"COORDS:xyz_coordinates {coords} are invalid, as they are not a list of floats"
            )

    im = get_glass_bg(tmpdir).copy()
    origin = (247, 207)
    scale = (2.6, 2.6)
    x, y, z = coords
    wpx = int(width * scale[0] / 2)
    wpy = int(width * scale[1] / 2)
    wlen = ((2 * wpx), (2 * wpy))
    try:
        xp = int(origin[0] + scale[0] * x)
        yp = int(origin[1] - scale[1] * y)
    except Exception as e:
        raise Exception(f"Coords:xyz_coordinates {coords} invalid: {e}")

    try:
        for xnum, xpos in enumerate(range(xp - wpx, xp + wpx)):
            for ynum, ypos in enumerate(range(yp - wpy, yp + wpy)):
                col = im[ypos, xpos, :] = [1, 0.17, 0, 1]
                if xnum <= 2 or xnum >= wlen[0] - 3 or ynum <= 2 or ynum >= wlen[1] - 3:
                    im[ypos, xpos, :] = [0, 0, 0, 1]
    except IndexError:
        im = get_glass_bg(tmpdir).copy()
        raise Exception(
            f"COORDS:xyz_coordinates at {coords} are out of bounds and can not be visualized"
        )
    axes.imshow(im)


@lru_cache(maxsize=1)
def get_glass_bg(tmpdir: Path):
    fname = (tmpdir / "background.png").expanduser().absolute()
    if not fname.exists():
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            display = plot_glass([], [0], colorbar=False)
            display.savefig(fname)
            print(f"COORDS: Initialized glass brain background in {fname}")
            display.close()
    else:
        print(f"COORDS: Reused glass brain background in {fname}")
    im = matplotlib.pyplot.imread(str(fname))
    return im


def plot_map(
    cachefiles: List[CacheFile], foo=lambda x: x, ignore_rejected=True, **kwargs
):
    """plot the whole map for a complete cachefile

    args
    ----
    cachefiles: List[CacheFile]
        a list of the cachefiles to be plotted
    foo: Callable
        will be applied to each value, and defaults to passing the
        original. But could be, e.g. lambda x : log10(x + 1) to plot logarithmized values
    ignore_rejected: bool 
        defaults to True, and ignores any traces which have been flagged for rejection. Alternatively, ignore the rejection and plot their values anyways.
    **kwargs
        additional keyword arguments are passed to :py:func:`~.plot_glass`


    returns
    -------
    display: the figure handle for the mapping plot
        

    """

    coords = []
    values = []
    uninspected = 0.0
    total = 0.0
    for cf in cachefiles:
        total += len(cf)
        for _, tattr in cf:
            if not ignore_rejected or not decode(tattr["reject"]):
                npk = decode(tattr["neg_peak_magnitude_uv"])
                ppk = decode(tattr["pos_peak_magnitude_uv"])
                if ppk is not None and npk is not None:
                    val = ppk - npk
                else:
                    val = 0
                    uninspected += 1.0

                xyz = decode(tattr["xyz_coords"])
                coords.append(xyz)
                values.append(val)

    rejected = total - len(values)
    print(f"This plot is based on {len(values)}/{total:3.0f} traces.")
    print(f"{rejected:3.0f} traces were rejected.")
    print(f"{uninspected:3.0f} traces were not inspected.")
    values = list(map(foo, values))
    return plot_glass(coords, values, **kwargs)


if __name__ == "__main__":
    pass
    # display = plot_glass([[0, 0, 0]], [1], colorbar=False)

    # coords = [
    #     [37.0, 54.2, 22.8],
    #     [37.1, 54.4, 22.1],
    #     [37.2, 53.9, 23.2],
    #     [37.2, 54.3, 21.9],
    # ]
    # values = [1000.0] * 4
    # display = plot_glass(coords, values)
    # M1 = [-36.6300, -17.6768, 54.3147]
    # plot_glass([M1], [1])

    # from pathlib import Path
    # from offspect.api import CacheFile, decode
    # from math import log10

    # path = Path("/home/rtgugg/Desktop/test-offspect/betti/inspected")
    # fname = path / "KaBe_ipsilesional_cmep_screening1.hdf5"
    # for fname in path.glob("*.hdf5"):
    #     cf = CacheFile(fname)
    #     plot_map(cf)
    #     display = plot_map(cf, foo=lambda x: log10(x + 1), ignore_rejected=False)

    #     display = plot_map(cf, foo=lambda x: log10(x + 1), ignore_rejected=False)
