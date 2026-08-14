from dataclasses import dataclass, field


@dataclass(frozen=True)
class S1ExportConfig:
    aoi_name: str
    aoi_bounds: tuple[float, float, float, float]  # format (west, south, east, north)
    start_date: str  # format: 'YYYY-MM-DD
    end_date: str  # format: 'YYYY-MM-DD
    dual_pol: bool = True  # polarisation values: ['VV', 'VH']
    bands: list[str] = field(default_factory=lambda: ["VV", "VH", "angle"])
    gcs_bucket: str | None = None
    scale_m: int = 10
    crs: str = "EPSG:4326"
    file_format: str = "GeoTIFF"
    max_pixels: int = int(1e8)

    # def __post_init__(self):
    # size of the aoi
    # lat range: -90 to 90
    # lon range: -180 to 180
    # start_date <= end_date


# def filter_image_collection(cfg: S1ExportConfig) -> ee.ImageCollection:
#     """"""
#     aoi_geom = ee.Geometry.Rectangle(cfg.aoi)
#     date_range = ee.DateRange(cfg.start_date, cfg.end_date)

#     image_collection = (
#         ee.ImageCollection("COPERNICUS/S1_GRD")
#         .filterBounds(aoi_geom)
#         .filterDate(date_range)
#         .filter(ee.Filter.eq("instrumentMode", ""IW""))
#         .filter(ee.Filter.eq("resolution_meters", 10))

#     )
#      if dual_pol:
#         .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
#         .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))

#     return image_collection

# def select_export_bands():
#     return NotImplementedError

# # image_ids = [image_info['id'] for image_info in info_s1['features']]
# # images = [ee.Image(image_id) for image_id in image_ids]


# def build_file_name_prefix()

# def build_export_task(cfg: S1ExportConfig):
#     return NotImplementedError

# # task = ee.batch.Export.image.toCloudStorage(
# #     image=image,
# #     description="Export SAR Sentinel-1",
# #     bucket=bucket_name,
# #     fileNamePrefix=filename,
# #     scale=resolution,  # Resolution in m per pixel. Default: 1000
# #     crs=image_crs,
# #     crsTransform=image_transform,
# #     region=region_of_interest,
# #     fileFormat=export_format,
# #     maxPixels=1e13,
# # )


if __name__ == "__main__":
    import hydra
    from dotenv import load_dotenv
    from hydra.core.config_store import ConfigStore
    from omegaconf import DictConfig

    load_dotenv()

    # ee.Authenticate()
    # ee.Initialize(project=os.getenv("project_id"))

    cs = ConfigStore.instance()

    @hydra.main(version_base=None, config_path="../../../configs", config_name="s1_export")
    def instantiate_config(cfg: DictConfig) -> None:
        # print(OmegaConf.to_yaml(cfg))

        export_cfg = S1ExportConfig(
            # collection=cfg.collection,
            aoi_name=cfg.aoi_name,
            aoi_bounds=tuple(cfg.aoi_bounds),
            start_date=cfg.start_date,
            end_date=cfg.end_date,
            gcs_bucket=cfg.gcs_bucket,
        )

        print(isinstance(export_cfg, S1ExportConfig))
        print(export_cfg)

    instantiate_config()

    # s1_collection = filter_image_collection(export_config)
    # s1_info = s1_collection.getInfo()
    # s1_collection_size = len(s1_info['features'])
    # print(s1_collection_size)
