import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.image import AxesImage


def plot_distribution(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None,
    ax: Axes | None = None,
) -> tuple:
    """Clip if values not None flatten the image band and plot its distribution"""
    if clip_min or clip_max:
        band = np.clip(band, clip_min, clip_max)
    band = band.flatten()
    if not ax:
        ax = plt.gca()
    return ax.hist(band, bins=100)


def clip_distribution(
    band: np.ndarray, clip_min: int | None = None, clip_max: int | None = None
) -> np.ndarray:
    """Clip the values of a 2D array and return a 1D array"""
    band = np.clip(band, clip_min, clip_max)
    return band


def plot_image(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None,
    ax: Axes | None = None,
) -> AxesImage:
    if clip_min or clip_max:
        band = np.clip(band, clip_min, clip_max)
    if not ax:
        ax = plt.gca()
    return ax.imshow(band, cmap="gray")


# TODO: find correct implementation
def plot_image_and_distribution(
    band: np.ndarray, clip_min: int | None = None, clip_max: int | None = None
) -> None:
    _, (ax1, ax2) = plt.subplots(ncols=2, figsize=(8, 4))
    plot_distribution(band, clip_min, clip_max, ax1)
    plot_image(band, clip_min, clip_max, ax2)
    plt.show()
