import sqlite3
import json
import os
import glob
import zipfile
import shutil

con = sqlite3.connect('location_data.db')
cursor = con.cursor()

#activity_segments table
cursor.execute('''
CREATE TABLE IF NOT EXISTS activity_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_timestamp TEXT,
    end_timestamp TEXT,
    start_latitude REAL,
    start_longitude REAL,
    end_latitude REAL,
    end_longitude REAL,
    distance_meters REAL,
    confidence TEXT,
    travel_mode TEXT
)
''')

#place_visits table
cursor.execute('''
CREATE TABLE IF NOT EXISTS place_visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    place_name TEXT,
    place_id TEXT,
    latitude REAL,
    longitude REAL,
    address TEXT,
    start_timestamp TEXT,
    end_timestamp TEXT,
    visit_confidence REAL
)
''')

# Converts coordinates from E7 format to decimal format
def convert_coords(lat, long):
    if lat is not None:
        lat /= 1e7
    if long is not None:
        long /= 1e7
    return lat, long

# Inserts an activity segment into the database
def insert_activity_segment(activity_segment, confidence_threshold):
    confidence = activity_segment.get('confidence', 'UNKNOWN').upper()

    # Skip if confidence is below threshold
    if confidence in ['LOW'] and confidence_threshold:
        return

    start_location = activity_segment.get('startLocation', {})
    start_latitude, start_longitude = convert_coords(
        start_location.get('latitudeE7'), start_location.get('longitudeE7'))

    end_location = activity_segment.get('endLocation', {})
    end_latitude, end_longitude = convert_coords(
        end_location.get('latitudeE7'), end_location.get('longitudeE7'))

    cursor.execute('''
    INSERT INTO activity_segments (
        start_timestamp, end_timestamp, start_latitude, start_longitude,
        end_latitude, end_longitude, distance_meters, confidence, travel_mode
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        activity_segment.get('duration', {}).get('startTimestamp'),
        activity_segment.get('duration', {}).get('endTimestamp'),
        start_latitude,
        start_longitude,
        end_latitude,
        end_longitude,
        activity_segment.get('distance'),
        confidence,
        activity_segment.get('waypointPath', {}).get('travelMode', None)
    ))

# Inserts a place visit into the database
def insert_place_visit(place_visit, confidence_threshold):
    visit_confidence = place_visit.get('visitConfidence', 0)

    # Skip if visit confidence is below threshold
    if visit_confidence < confidence_threshold:
        return

    location = place_visit.get('location', {})
    latitude, longitude = convert_coords(location.get('latitudeE7'), location.get('longitudeE7'))

    cursor.execute('''
    INSERT INTO place_visits (
        place_name, place_id, latitude, longitude, address,
        start_timestamp, end_timestamp, visit_confidence
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        location.get('name'),
        location.get('placeId'),
        latitude,
        longitude,
        location.get('address'),
        place_visit.get('duration', {}).get('startTimestamp'),
        place_visit.get('duration', {}).get('endTimestamp'),
        place_visit.get('visitConfidence')
    ))

def process_file(file_path, confidence_threshold):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    if 'timelineObjects' not in data:
        print(f"'timelineObjects' not found in {file_path}. Skipping.")
        return

    for entry in data.get('timelineObjects', []):
        if 'activitySegment' in entry:
            insert_activity_segment(entry['activitySegment'], confidence_threshold)
        elif 'placeVisit' in entry:
            insert_place_visit(entry['placeVisit'], confidence_threshold)

def process_zip(zip_path, extract_to='data', confidence_threshold=50):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    semantic_path = os.path.join(extract_to, "Takeout", "Location History", "Semantic Location History")
    
    if os.path.exists(semantic_path):
        for root, _, files in os.walk(semantic_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    print(f"Processing {file_path}")
                    process_file(file_path, confidence_threshold)
                    
                    # Move extracted json files
                    new_file_path = os.path.join('data', os.path.basename(file_path))
                    shutil.move(file_path, new_file_path)
                    print(f"Moved {file_path} to {new_file_path}")
   
    for folder_name in ['__MACOSX', 'Takeout']:
        folder_path = os.path.join(extract_to, folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
#gets all json files from folder named data
folder_path = 'data'
confidence_threshold = 50 # Confidence threshold for filtering out low confidence entries
for zip_file in glob.glob(os.path.join(folder_path, '*.zip')):
    process_zip(zip_file, confidence_threshold=confidence_threshold)

con.commit()
con.close()