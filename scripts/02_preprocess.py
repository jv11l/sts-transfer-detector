import os
from sar_sts_detection.utils.masks import (
    apply_mask_to_image,
    create_file_path,
    get_image_crs,
    load_raster_image,
    load_shapefile_into_gdf,
    make_ocean_mask_for_area_of_interest,
    save_raster_image,
    transform_ocean_mask_to_image_crs,
)
from sar_sts_detection.config import (
    MASKED_IMAGE_DIR,
    RAW_IMAGE_DIR,
    GEODATA_DIR,
    AREA_OF_INTEREST,
    COUNTRY
)

def mask():
    eez_boundaries_file = create_file_path("eez_v12.shp", GEODATA_DIR)  # Downloaded from Martime Regions website
    print(f"Loading EEZ boundaries file {eez_boundaries_file}")
    gdf_eez_boundaries = load_shapefile_into_gdf(
        eez_boundaries_file
    )
    print(f"Making ocean mask for the area {AREA_OF_INTEREST} in {COUNTRY}")
    gdf_ocean_mask = make_ocean_mask_for_area_of_interest(
        gdf_eez_boundaries,
        AREA_OF_INTEREST,
        COUNTRY
    )
    image_file = create_file_path(os.listdir(RAW_IMAGE_DIR)[1], RAW_IMAGE_DIR)
    print(f"Loading raster image {image_file}")
    band, meta = load_raster_image(image_file)
    print(band.shape)
    image_crs = get_image_crs(image_file)
    print(f"Projecting ocean mask to the image CRS: {meta['crs']}")
    gdf_ocean_mask = transform_ocean_mask_to_image_crs(image_crs, gdf_ocean_mask)
    print("Applying ocean mask to image")
    out_image, out_transform = apply_mask_to_image(image_file, gdf_ocean_mask)
    print(f"Saving masked image to {MASKED_IMAGE_DIR}")
    save_raster_image("masked_image.tif", MASKED_IMAGE_DIR, out_image, out_transform)


if __name__ == "__main__":
    mask()
