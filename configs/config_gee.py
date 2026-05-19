from dotenv import load_dotenv
import os

load_dotenv()

class ExportConfig:
    def __init__(self):
        PROJECT_ID = os.environ.get('STS_TRANSFER_PROJECT_ID')
        BUCKET_ID = os.environ.get('STS_TRANSFER_BUCKET_ID')  # REPLACE ENVIRONMENT VARIABLE
        LIMIT_TASK_QUOTA = 2
        DEST_FOLDER = 'SAR_TIFF'
        REGION_OF_INTEREST = [22.357, 36.373, 23.114, 36.846]  # Laconian bay
        RESOLUTION = 10  # meters per pixel

    def get_config(self):
        print(self.__dict__)
        return {key: value for key, value in self.__dict__.items()}
            
            
    
# Define the region of interest

# Define the date range
start_date = '2022-01-01'
end_date = '2023-03-01'

# Define the band
band = 'VH'

# Definde destination folder

# Credentials to access bucket
# PATH = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

# Instantiate Storage Client
# storage_client = storage.Client(PATH)
# bucket = storage_client.get_bucket(bucket_id)

if __name__ == "__main__":
    export_config = Config()
    export_settings = export_config.get_config()
    print(export_settings)