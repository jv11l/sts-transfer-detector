import hydra
from omegaconf import DictConfig

from sar_sts_detection.data.preprocessing import create_mask_gdf, preprocess_tile


@hydra.main(version_base=None, config_path="../configs", config_name="config")
def preprocess(cfg: DictConfig) -> None:
    """Create a mask to remove land from tile and apply mask to tile"""
    mask_gdf = create_mask_gdf(
        eez_shapefile=cfg.resources.eez_geodata,
        aoi_bounds=tuple(cfg.preprocessing.masking.aoi_bounds),
    )

    preprocess_tile(
        input_folder=cfg.paths.raw_dir,
        output_folder=cfg.paths.masked_dir,
        mask_gdf=mask_gdf,
    )


if __name__ == "__main__":
    preprocess()
