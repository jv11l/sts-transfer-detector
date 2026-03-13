import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from pathlib import Path
import rasterio
from rasterio import CRS
from shapely.geometry import box


###================ Plot helper functions =================###

def plot_backscatter_distribution(
    band_db: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None
    ) -> Axes:
    """Clip if values not None flatten the image band and plot its distribution"""
    clip_distribution(band_db, clip_min, clip_max)
    ax = plt.gca()
    ax.hist(band_db, bins=100)
    ax.set_title("Distribution of backscatter (dB)")
    return ax
    
def clip_distribution(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None
    ) -> np.ndarray:
    """Clip the values of a 2D array and return a 1D array"""
    band = np.clip(band, clip_min, clip_max)
    return band.flatten()
    
    
def show_image(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None
    ) -> Axes:
    band = clip_distribution(band, clip_min, clip_max)
    ax = plt.gca()
    ax.imshow(band, cmap='gray')
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
    
###================ File helper functions =================###

def get_file_path(file: str, folder: Path) -> Path:
    path_to_file = folder/file    
    if not path_to_file.exists():
        raise FileExistsError("File not found")
    return path_to_file


def read_shapefile_into_geodataframe(
    file: Path,
    ) -> gpd.GeoDataFrame:
    # Read the shapefile: Worlds' Exclusive Economic Zone
    if not file.exists():
        raise FileExistsError("File not found.")
    return gpd.read_file(file)


###================ GeoData helper functions =================###

def load_image_from_gcs():
    raise NotImplementedError

def read_image_band_from_local_file(
    file: Path,
    ) -> np.ndarray:
    """Read raster image band from TIFF image in local folder"""
    if not file.exists():
        raise FileExistsError("File not found")
    with rasterio.open(file) as f:
        band_db = f.read(1)
    return band_db

def get_image_crs(file: Path) -> rasterio.CRS:
    """"""
    if not file.exists():
        raise FileExistsError("File not found")
    with rasterio.open(file) as img:
        return img.crs

def get_image_metadata(file: Path) -> dict:
    """"""
    if not file.exists():
        raise FileExistsError("File not found")
    with rasterio.open(file) as img:
        return img.meta
    