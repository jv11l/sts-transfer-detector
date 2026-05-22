from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask as rasterio_mask
from shapely.geometry import box


def create_file_path(filename: str, folder: Path) -> Path:
    path_to_file = folder / filename
    if not path_to_file.exists():
        raise FileNotFoundError
    return path_to_file


def load_raster_file(file: Path) -> tuple[np.ndarray, dict]:
    with rasterio.open(file) as src:
        band: np.ndarray = src.read(1)
        meta: dict = src.meta.copy()
        # crs: rasterio.CRS = src.crs
    return band, meta  # , crs


def load_geodf(file: Path) -> gpd.GeoDataFrame:
    if not file.exists():
        raise FileNotFoundError
    return gpd.read_file(file)


def transform_mask_crs(
    dest_crs: rasterio.CRS,
    mask_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    return mask_gdf.to_crs(dest_crs)


def apply_mask(
    raster_file: Path,
    mask_gdf: gpd.GeoDataFrame,
) -> tuple[np.ndarray, dict]:
    with rasterio.open(raster_file) as src:
        out_image, out_transform = rasterio_mask(
            src,
            mask_gdf.geometry,
            nodata=np.nan,
            crop=True,
            indexes=1,
        )
        out_meta = src.meta.copy()
        out_meta.update(
            {
                "driver": "GTiff",
                "height": out_image.shape[0],
                "width": out_image.shape[1],
                "transform": out_transform,
            }
        )
    return out_image, out_meta


def save_raster_image(
    out_filename: str,
    out_dir: Path,
    out_image: np.ndarray,
    out_meta: dict,
) -> None:
    with rasterio.open(out_dir / out_filename, "w", **out_meta) as dest:
        dest.write(out_image, 1)


def create_mask_gdf(
    eez_shapefile: Path, aoi_bounds: tuple[float, float, float, float]
) -> gpd.GeoDataFrame:
    aoi_bbox = box(*aoi_bounds)
    eez_gdf = gpd.read_file(eez_shapefile, bbox=aoi_bbox)
    mask_gdf = gpd.clip(eez_gdf, mask=aoi_bounds)
    if mask_gdf.empty:
        raise ValueError("Mask geometry is empty!")
    return mask_gdf


def preprocess_tile(
    input_folder: str,
    output_folder: str,
    mask_gdf: gpd.GeoDataFrame,
) -> None:
    for tile in Path(input_folder).iterdir():
        _, meta = load_raster_file(tile)
        image_crs = meta["crs"]
        mask_gdf = transform_mask_crs(image_crs, mask_gdf)
        out_image, out_transform = apply_mask(tile, mask_gdf)
        output_file = f"{tile.stem}-preprocessed{tile.suffix}"
        save_raster_image(output_file, Path(output_folder), out_image, out_transform)
        break


if __name__ == "__main__":
    import hydra
    from omegaconf import DictConfig

    @hydra.main(version_base=None, config_path="../../../configs", config_name="config")
    def preprocess(cfg: DictConfig) -> gpd.GeoDataFrame:
        aoi_bounds = tuple(cfg.preprocessing.masking.aoi_bounds)
        print(aoi_bounds)
        print(type(aoi_bounds))
        mask_gdf = create_mask_gdf(
            eez_shapefile=cfg.resources.eez_geodata,
            aoi_bounds=tuple(cfg.preprocessing.masking.aoi_bounds),
        )
        return mask_gdf

    preprocess()
