import geopandas as gpd
import numpy as np
from pathlib import Path
import rasterio
from rasterio.mask import mask
from shapely.geometry import box

# File manipulation
def create_file_path(filename: str, dir: Path) -> Path:
    """Get the path to a file in a folder, raise an error if the file does not exist"""
    path_to_file = dir / filename
    if not path_to_file.exists():
        raise FileExistsError("File not found")
    return path_to_file

# Raster image 
def load_raster_image(file: Path) -> tuple[np.ndarray, dict]:
    """Load raster image from TIFF image"""
    with rasterio.open(file) as src:
        band = src.read(1)
        meta = src.meta.copy()
    return band, meta

# TODO: merge into load_raster_image?
def get_image_crs(file: Path) -> rasterio.CRS:
    """"""
    with rasterio.open(file) as src:
        return src.crs

def apply_mask_to_image(
    file: Path,
    ocean_mask: gpd.GeoDataFrame,
    ) -> tuple[np.ndarray, dict]:
    # Clip the TIFF image using the MultiPolygon geometry
    with rasterio.open(file) as src:
        out_image, out_transform = mask(
            src, 
            ocean_mask.geometry, 
            nodata=np.nan, 
            crop=True, 
            indexes=1
        )
        # Update image metadata
        out_meta = src.meta.copy()
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[0],
                         "width": out_image.shape[1],
                         "transform": out_transform})
    return out_image, out_meta

def map_db_to_pixels(image: np.ndarray, db_range: tuple[int]) -> np.ndarray:
    return out_image

def save_raster_image(
    out_filename: str,
    out_dir: Path,
    out_image: np.ndarray,
    out_meta: dict
    ) -> None:
    """Save a raster image to a TIFF file."""
    with rasterio.open(out_dir / out_filename, "w", **out_meta) as dest:
        dest.write(out_image, 1)


# GeoData
def load_shapefile_into_gdf(
    file: Path,
    ) -> gpd.GeoDataFrame:
    # Read the shapefile: Worlds' Exclusive Economic Zone
    if not file.exists():
        raise FileExistsError("File not found.")
    return gpd.read_file(file)

# TODO: make it a general function - aumatic selection of EEZ based on input AOI
## Non-null interections of aoi with geoms in df -> df of selected EEZ
## Union of the geometries after clipping
## Save infos about the AOI? area, countries' EEZ and proportion
# TODO: fix index reset
# NOTE: Assumes that area is included in EEZ of country
def make_ocean_mask_for_area_of_interest(
    eez_boundaries: gpd.GeoDataFrame, 
    area: list,
    country: str
    ) -> gpd.GeoDataFrame:
    """Create an ocean mask for the area of interest."""
    # Filter DataFrame for the selected country e.g. Greece
    country_filter = eez_boundaries["TERRITORY1"] == country 
    eez_greece = eez_boundaries.loc[country_filter].copy()
    eez_greece = eez_boundaries.reset_index()  # FIXIT: index not reset!
    
    # Create a bounding box geometry of the Area of Interest (AOI) e.g. Laconian Bay
    aoi_bbox = box(*area)
    
    # Clip the GeoDataFrame to the bounding box of the AOI
    ocean_mask = gpd.clip(eez_greece, mask=aoi_bbox)
    if ocean_mask.empty:
        raise ValueError("Geometry of the ocean mask is empty!")
    return ocean_mask


def transform_ocean_mask_to_image_crs(
    image_crs: rasterio.CRS,
    ocean_mask: gpd.GeoDataFrame
    ) -> gpd.GeoDataFrame:
    ocean_mask = ocean_mask.to_crs(image_crs)
    return ocean_mask
