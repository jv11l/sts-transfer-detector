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


def create_mask(
    src_file: Path, out_file: Path, aoi_bounds: tuple[float, float, float, float]
) -> None:
    aoi_bbox = box(*aoi_bounds)
    gdf_src = gpd.read_file(src_file, bbox=aoi_bbox)
    gdf_mask = gpd.clip(gdf_src, mask=aoi_bounds)
    if gdf_mask.empty:
        raise ValueError("Mask geometry is empty!")
    gdf_mask.to_file(filename=out_file)


def preprocess_tile(
    input_folder: str,
    output_folder: str,
    mask_geodata: str,
) -> None:
    gdf_mask = load_geodf(Path(mask_geodata))
    for tile in Path(input_folder).iterdir():
        _, meta = load_raster_file(tile)
        image_crs = meta["crs"]
        gdf_mask = transform_mask_crs(image_crs, gdf_mask)
        out_image, out_transform = apply_mask(tile, gdf_mask)
        output_file = f"{tile.stem}-preprocessed{tile.suffix}"
        save_raster_image(output_file, Path(output_folder), out_image, out_transform)
        break


if __name__ == "__main__":
    import hydra
    from omegaconf import DictConfig

    @hydra.main(version_base=None, config_path="../../../configs", config_name="config")
    def preprocess(cfg: DictConfig) -> None:
        aoi_bounds = tuple(cfg.preprocessing.masking.aoi_bounds)
        print(aoi_bounds)
        print(type(aoi_bounds))
        create_mask(
            src_file=cfg.resources.eez_geodata,
            out_file=cfg.resources.mask_geodata,
            aoi_bounds=tuple(cfg.preprocessing.masking.aoi_bounds),
        )

    preprocess()
