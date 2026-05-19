from osgeo import gdal, osr
from typing import Tuple


def pixel_to_coordinates(
    geotiff_file: str,
    pixel_x: int,
    pixel_y: int
    ) -> Tuple[float, float]:
    """
    Convert pixel coordinates to geographical coordinates.

    Args:
        geotiff_file (str): Path to the GeoTIFF file.
        pixel_x (int): The x-coordinate of the pixel.
        pixel_y (int): The y-coordinate of the pixel.

    Returns:
        tuple: The geographical coordinates corresponding to the pixel coordinates.

    Raises:
        FileNotFoundError: If the GeoTIFF file cannot be opened.
        ValueError: If the GeoTIFF file does not have a valid geotransform.
    """
    dataset = gdal.Open(geotiff_file)
    
    if dataset is None:
        raise FileNotFoundError("Could not open GeoTIFF file")
    
    geotransform = dataset.GetGeoTransform()
    
    if geotransform is None:
        raise ValueError("GeoTIFF file does not have a valid geotransform")
    
    origin_x = geotransform[0]
    origin_y = geotransform[3]
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]
    x = origin_x + pixel_x * pixel_width
    y = origin_y + pixel_y * pixel_height
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromWkt(dataset.GetProjection())
    transform = osr.CoordinateTransformation(spatial_ref, spatial_ref.CloneGeogCS())
    point = transform.TransformPoint(x, y)
    return point[0], point[1]