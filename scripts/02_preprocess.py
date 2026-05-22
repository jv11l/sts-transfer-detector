import hydra
from omegaconf import DictConfig

from sar_sts_detection.data.preprocessing import create_mask, preprocess_tile


@hydra.main(version_base=None, config_path="../configs", config_name="config")
def preprocess(cfg: DictConfig) -> None:
    """Create a mask to remove land parts from tile and prepocess it"""
    create_mask(
        src_file=cfg.resources.eez_geodata,
        out_file=cfg.resources.mask_geodata,
        aoi_bounds=tuple(cfg.preprocessing.masking.aoi_bounds),
    )

    preprocess_tile(
        input_folder=cfg.paths.raw_dir,
        output_folder=cfg.paths.masked_dir,
        mask_geodata=cfg.resources.mask_geodata,
    )


if __name__ == "__main__":
    preprocess()
