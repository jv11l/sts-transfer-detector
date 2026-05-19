import geopandas as gpd
from matplotlib.image import AxesImage
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np


###================ Plot helper functions =================###

def plot_distribution(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None,
    ax: Axes | None = None
    ) -> tuple:
    """Clip if values not None flatten the image band and plot its distribution"""
    if clip_min or clip_max:
        band = np.clip(band, clip_min, clip_max)
    band = band.flatten()
    if not ax:
        ax = plt.gca()
    return ax.hist(band, bins=100)

    
def plot_image(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None,
    ax: Axes | None = None
    ) -> AxesImage:
    if clip_min or clip_max:
        band = np.clip(band, clip_min, clip_max)
    if not ax:
        ax = plt.gca()
    return ax.imshow(band, cmap='gray')


# TODO: find correct implementation 
def plot_image_and_distribution(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None
    ) -> None:
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(8, 4))
    plot_distribution(band, clip_min, clip_max, ax1)
    plot_image(band, clip_min, clip_max, ax2)
    plt.show()
    
    
if __name__ == "___main___":
    import os
    from sts.config import RAW_IMAGE_DIR
    from sts.utils import create_file_path, load_raster_image
    
    raw_image_filepath = create_file_path(os.listdir(RAW_IMAGE_DIR)[0], RAW_IMAGE_DIR)
    image, meta = load_raster_image(raw_image_filepath)
    plot_image_and_distribution(image)
    