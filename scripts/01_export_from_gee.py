import datetime
from collections import Counter
import ee
from google.cloud import storage
import json
import os
import time
import sys

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
sys.path.insert(0, './utils')

from gee import (
    # generate_date_range,
    get_image_collection,
    get_image_list, 
    len_image_list, 
    get_image_from_list,
    get_image_id,
)
from export import (
    export_image_to_gcs,
    update_task_statuses,
    update_task_states_counts,
)


if __name__ == '__main__':
    # Authenticate and initialise Earth Engine project
    ee.Authenticate()
    ee.Initialize(
        project=project_id,
        opt_url='https://earthengine-highvolume.googleapis.com'  # for large volumes
    )

    # Get the image collection for the selected aoi, date range and band
    image_collection = get_image_collection(aoi, (start_date, end_date), band)
    image_list = get_image_list(image_collection)
    image_list_size = len_image_list(image_list)

    # Start the export task
    # TODO: check for already running tasks
    task_statuses = {}
    tasks = []
    task_counts = len(tasks)
    counts_running = 0
    counts_ready = 0

    print("Start of export!")
    while task_counts < image_list_size:
        if (counts_running + counts_ready) < TASK_QUOTA:
            # Export the image to Google Cloud Storage
            image = get_image_from_list(image_list, task_counts)
            image_id = get_image_id(image)
            if f'{image_id}.tif' not in os.listdir('data/sar-sentinel-1-tiff/VH'):  # REPLACE PATH
                print(f"Exporting image {image_id} to Google Cloud Storage")
                task = export_image_to_gcs(
                    image,
                    bucket_id,
                    folder_name,
                    region_of_interest=aoi,
                    resolution=10)  # CHANGE RESOLUTION to 10 for RAW images
                tasks.append(task)
            else:
                print(f"Image {image_id} already exists in Google Cloud Storage")
            
            # Get the next image
            task_counts += 1
            image = get_image_from_list(image_list, task_counts)
            
            # Update task statuses
            task_statuses = update_task_statuses(tasks, task_statuses)
            
            # Update task state counts
            counts_completed, counts_failed, counts_running, counts_ready = update_task_states_counts(task_statuses)
            print(f"Ready: {counts_ready}, Running: {counts_running}, \
                  Completed: {counts_completed}/{image_list_size}, Failed: {counts_failed}")
            time.sleep(5)
            print("===============================================")
        else:
            # Update task state counts
            print("Waiting for a running task to complete before starting a new one...")
            task_statuses = update_task_statuses(tasks, task_statuses)
            counts_completed, counts_failed, counts_running, counts_ready = update_task_states_counts(task_statuses)
            print(f"Ready: {counts_ready}, Running: {counts_running}, Completed: {counts_completed}/{image_list_size}, Failed: {counts_failed}")
            time.sleep(60)
            print("===============================================")
    
    while (counts_running + counts_ready) > 0:
        print("Finalising exports...")
        task_statuses = update_task_statuses(tasks, task_statuses)
        counts_completed, counts_failed, counts_running, counts_ready = update_task_states_counts(task_statuses)
        print(f"Ready: {counts_ready}, Running: {counts_running}, Completed: {counts_completed}/{image_list_size}, Failed: {counts_failed}")
        time.sleep(60)
        print("===============================================")
    
    print("End of export!")
    task_statuses = update_task_statuses(tasks, task_statuses)
    counts_completed, counts_failed, counts_running, counts_ready = update_task_states_counts(task_statuses)
    print(f"Ready: {counts_ready}, Running: {counts_running}, Completed: {counts_completed}, Failed: {counts_failed}")
    print("===============================================")
    
    # Write final task statuses to a JSON file
    with open(f'logs/task_statuses.json', 'w') as f:
        json.dump(task_statuses, f)
        