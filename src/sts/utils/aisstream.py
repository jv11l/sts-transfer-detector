import asyncio
import csv
from datetime import datetime, timezone
import os
import json
import websockets

STREAM_URL = "wss://stream.aisstream.io/v0/stream"
API_KEY = os.environ.get("AISSTREAM_KEY")
BBOX = [[[19, 30.5], [42, 46.8]]]

# Batch size for database inserts
BATCH_SIZE = 10

# List to hold messages before batch insert
messages_batch = []


async def connect_ais_stream():
    # Send a subscription message to create a connection to the stream
    async with websockets.connect(STREAM_URL) as websocket:
        # Define a subscription message
        subscribe_message = {
            "APIKey": API_KEY,  # Required!
            "BoundingBoxes": BBOX,  # Required! (left,bottom,right,top)
            # "FiltersShipMMSI": ["368207620", "367719770", "211476060"], # Optional!
            #  "FilterMessageTypes": ["PositionReport"]} # Optional!
        }
        # Dump the message into a JSON file
        subscribe_message_json = json.dumps(subscribe_message)
        # Send the subscirption message to Websocket. Must be sent within 3 sec!
        await websocket.send(subscribe_message_json)

        csv_file = open('ais_data.csv', 'a', newline='')
        writer = csv.writer(csv_file)
        HEADER = False
        
        # Get messages from websocket
        async for message_json in websocket:
            global messages_batch
            message = json.loads(message_json)  # Convert JSON strings into py dict
            message_type = message["MessageType"]
            
            if message_type == 'PositionReport':
                ais_message = message['Message']['PositionReport']
                header = ais_message.keys()
                messages_batch.append(ais_message)
                if not HEADER:
                    writer.writerow(header)
                    HEADER = True
                if len(messages_batch) >= BATCH_SIZE:
                    # Assuming json_data is a list of dictionaries
                    for msg in messages_batch:
                        # Write each item as a row in the CSV file
                        print(msg)
                        writer.writerow(msg.values())
                    csv_file.close()
                    await websocket.close()

       
if __name__ == "__main__":
    asyncio.run(asyncio.run(connect_ais_stream()))