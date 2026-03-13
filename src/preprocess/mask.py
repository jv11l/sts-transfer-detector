import geopandas as gpd
import numpy as np
import os
from pathlib import Path
import rasterio
from rasterio.mask import mask
from shapely.geometry import box
from utils.utils import (
    get_file_path,
    get_image_crs,
    get_image_metadata,
    read_shapefile_into_geodataframe,
    read_image_band_from_local_file,
    show_image
)

DATA_FOLDER = Path("../../data")
IMAGE_FOLDER: Path = DATA_FOLDER/"SAR_TIFF"
GEODATA_FOLDER: Path = DATA_FOLDER/"World_EEZ_v12_20231025"
AREA_OF_INTEREST: list = [22.357, 36.373, 23.114, 36.846]
COUNTRY_OF_INTEREST: str = "Greece"
EEZ_WORLD_BOUNDARIES: str = "eez_v12.shp"  


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


def apply_ocean_mask_to_image(
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
        image_meta = get_image_metadata(file)
        out_meta = image_meta.copy()
        out_meta.update({"driver": "GTiff",
                            "height": out_image.shape[0],
                            "width": out_image.shape[1],
                            "transform": out_transform})
    return out_image, out_meta



if __name__ == "__main__":
    image_file = get_file_path(os.listdir(IMAGE_FOLDER)[1], IMAGE_FOLDER)
    print(f"Reading image {image_file}")
    band_db = read_image_band_from_local_file(image_file)
    print(band_db.shape)
    
    eez_boundaries_file = get_file_path("eez_v12.shp", GEODATA_FOLDER)  # Downloaded from Martime Regions website
    print(f"Reading EEZ boundaries file {eez_boundaries_file}")
    gdf_eez_boundaries = read_shapefile_into_geodataframe(
        eez_boundaries_file,
    )
    print(f"Making ocean mask for the area {AREA_OF_INTEREST} in {COUNTRY_OF_INTEREST}")
    gdf_ocean_mask = make_ocean_mask_for_area_of_interest(
        gdf_eez_boundaries,
        AREA_OF_INTEREST,
        COUNTRY_OF_INTEREST
    )
    image_crs = get_image_crs(image_file)
    print(f"Projecting ocean mask to the image CRS")
    gdf_ocean_mask = transform_ocean_mask_to_image_crs(image_crs, gdf_ocean_mask)
    print("Applying ocean mask to image")
    out_image, out_transform = apply_ocean_mask_to_image(image_file, gdf_ocean_mask)
    # print("Show transformed image")
    # show_image(out_image)
