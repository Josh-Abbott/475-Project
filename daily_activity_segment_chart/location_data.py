import sqlite3
import json
import os
import glob

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

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry in data.get('timelineObjects', []):
        if 'activitySegment' in entry:
            activity_segment = entry['activitySegment']

            start_location = activity_segment.get('startLocation', {})
            start_latitude = start_location.get('latitudeE7')
            start_longitude = start_location.get('longitudeE7')

            if start_latitude is not None:
                start_latitude /= 1e7
            else:
                start_latitude = None

            if start_longitude is not None:
                start_longitude /= 1e7
            else:
                start_longitude = None

            end_location = activity_segment.get('endLocation', {})
            end_latitude = end_location.get('latitudeE7')
            end_longitude = end_location.get('longitudeE7')

            if end_latitude is not None:
                end_latitude /= 1e7
            else:
                end_latitude = None

            if end_longitude is not None:
                end_longitude /= 1e7
            else:
                end_longitude = None

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
                activity_segment.get('confidence'),
                activity_segment.get('waypointPath', {}).get('travelMode', None)
            ))

        elif 'placeVisit' in entry:
            place_visit = entry['placeVisit']
            location = place_visit.get('location', {})

            latitude = location.get('latitudeE7')
            longitude = location.get('longitudeE7')

            if latitude is not None:
                latitude /= 1e7
            else:
                latitude = None

            if longitude is not None:
                longitude /= 1e7
            else:
                longitude = None

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

#gets all json files from folder named data
folder_path = 'data'
json_files = glob.glob(os.path.join(folder_path, '*.json'))

for file in json_files:
    process_file(file)

con.commit()
con.close()