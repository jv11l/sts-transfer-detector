import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np


###================ Plot helper functions =================###

def plot_backscatter_distribution(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None
    ) -> Axes:
    """Clip if values not None flatten the image band and plot its distribution"""
    if clip_min or clip_max:
        band = clip_distribution(band, clip_min, clip_max)
    band = band.flatten()
    ax = plt.gca()
    ax.hist(band, bins=100)
    ax.set_title("Distribution of backscatter (dB)")
    plt.show()
    return ax
    
def clip_distribution(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None
    ) -> np.ndarray:
    """Clip the values of a 2D array and return a 1D array"""
    band = np.clip(band, clip_min, clip_max)
    return band
    
def show_image(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None
    ) -> Axes:
    if clip_min or clip_max:
        band = clip_distribution(band, clip_min, clip_max)
    ax = plt.gca()
    ax.imshow(band, cmap='gray')
    plt.show()
    return ax

# TODO: find correct implementation 
def plot_image_and_distribution(
    band: np.ndarray,
    clip_min: int | None,
    clip_max: int | None
    ) -> None:
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(8, 4))
    ax1 = plot_backscatter_distribution(band, clip_min, clip_max)
    ax2 = show_image(band, clip_min, clip_max)
    plt.show()