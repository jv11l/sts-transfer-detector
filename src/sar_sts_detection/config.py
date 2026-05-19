from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR: Path = PROJECT_ROOT / "data"
IMAGE_DIR: Path = DATA_DIR / "images"
RAW_IMAGE_DIR: Path = IMAGE_DIR / "raw"
MASKED_IMAGE_DIR: Path = IMAGE_DIR / "masked"
PROCESSED_IMAGE_DIR: Path = IMAGE_DIR / "processed"
AIS_DIR: Path = DATA_DIR / "ais"
SAMPLE_AIS_DIR: Path = AIS_DIR / "Spire_sample"
GEODATA_DIR: Path = DATA_DIR / "World_EEZ_v12_20231025"

# Constants
AREA_OF_INTEREST: list = [22.357, 36.373, 23.114, 36.846]
COUNTRY: str = "Greece"
# EEZ_BOUNDARIES: str = "eez_v12.shp"

if __name__ == "__main__":
    print(PROJECT_ROOT)
    