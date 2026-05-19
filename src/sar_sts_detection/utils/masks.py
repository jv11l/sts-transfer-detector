import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from pathlib import Path
import rasterio
from rasterio import CRS
from rasterio.mask import mask as rasterio_mask
from shapely.geometry import box


###================ Plot helper functions =================###

def plot_backscatter_distribution(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None
    ) -> Axes:
    """Clip if values not None flatten the image band and plot its distribution"""
    band_db = clip_distribution(band, clip_min, clip_max)
    band_db = band_db.flatten()
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
    return band
    
def show_raster_image(
    band: np.ndarray,
    clip_min: int | None = None,
    clip_max: int | None = None
    ) -> Axes:
    band_db = clip_distribution(band, clip_min, clip_max)
    ax = plt.gca()
    ax.imshow(band_db, cmap='gray')
    return ax

# TODO: find correct implementation 
def plot_image_and_distribution(
    band: np.ndarray,
    clip_min: int | None,
    clip_max: int | None
    ) -> None:
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(8, 4))
    ax1 = plot_backscatter_distribution(band, clip_min, clip_max)
    ax2 = show_raster_image(band, clip_min, clip_max)
    plt.show()
    
###================ File helper functions =================###

def get_file_path(file: str, folder: Path) -> Path:
    path_to_file = folder / file
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

def save_image_png(image: np.ndarray, file: Path):
    plt.imsave(file, image, cmap='gray')

###================ GeoData helper functions =================###

def load_image_from_gcs():
    raise NotImplementedError

def read_raster_image_band(
    file_path: Path,
    ) -> np.ndarray:
    """Read raster image band from TIFF image"""
    with rasterio.open(file_path) as f:
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


###================ Mask pipeline functions =================###

def create_file_path(filename: str, dir: Path) -> Path:
    path_to_file = dir / filename
    if not path_to_file.exists():
        raise FileExistsError("File not found")
    return path_to_file


def load_raster_image(file: Path) -> tuple[np.ndarray, dict]:
    with rasterio.open(file) as src:
        band = src.read(1)
        meta = src.meta.copy()
    return band, meta


def load_shapefile_into_gdf(file: Path) -> gpd.GeoDataFrame:
    if not file.exists():
        raise FileExistsError("File not found.")
    return gpd.read_file(file)


def make_ocean_mask_for_area_of_interest(
    eez_boundaries: gpd.GeoDataFrame,
    area: list,
    country: str,
) -> gpd.GeoDataFrame:
    country_filter = eez_boundaries["TERRITORY1"] == country
    eez_country = eez_boundaries.loc[country_filter].copy()
    eez_country = eez_boundaries.reset_index()
    aoi_bbox = box(*area)
    ocean_mask = gpd.clip(eez_country, mask=aoi_bbox)
    if ocean_mask.empty:
        raise ValueError("Geometry of the ocean mask is empty!")
    return ocean_mask


def transform_ocean_mask_to_image_crs(
    image_crs: rasterio.CRS,
    ocean_mask: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    return ocean_mask.to_crs(image_crs)


def apply_mask_to_image(
    file: Path,
    ocean_mask: gpd.GeoDataFrame,
) -> tuple[np.ndarray, dict]:
    with rasterio.open(file) as src:
        out_image, out_transform = rasterio_mask(
            src,
            ocean_mask.geometry,
            nodata=np.nan,
            crop=True,
            indexes=1,
        )
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[0],
            "width": out_image.shape[1],
            "transform": out_transform,
        })
    return out_image, out_meta


def save_raster_image(
    out_filename: str,
    out_dir: Path,
    out_image: np.ndarray,
    out_meta: dict,
) -> None:
    with rasterio.open(out_dir / out_filename, "w", **out_meta) as dest:
        dest.write(out_image, 1)
    