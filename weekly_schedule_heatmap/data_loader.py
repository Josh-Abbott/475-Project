import os
import glob
import json
import pandas as pd
import numpy as np

def load_data(folder_path='data', start_period='2020-01-01', end_period='2020-12-31'):
    records = []

    json_files = glob.glob(os.path.join(folder_path, '*.json'))
    print(f"Found {len(json_files)} JSON files.")

    for file_path in json_files:
        print(f"Processing file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for entry in data.get('timelineObjects', []):
            if 'placeVisit' in entry:
                place_visit = entry['placeVisit']
                location = place_visit.get('location', {})

                place_name = location.get('name')
                start_timestamp = place_visit.get('duration', {}).get('startTimestamp')
                end_timestamp = place_visit.get('duration', {}).get('endTimestamp')

                start_datetime = pd.to_datetime(start_timestamp, errors='coerce', utc=True)
                end_datetime = pd.to_datetime(end_timestamp, errors='coerce', utc=True)

                if pd.isnull(start_datetime) or pd.isnull(end_datetime):
                    continue

                records.append({
                    'place_name': place_name,
                    'start_datetime': start_datetime,
                    'end_datetime': end_datetime
                })

    place_visits = pd.DataFrame(records)
    print(f"Total place visits loaded: {len(place_visits)}")

    if place_visits.empty:
        print("No place visits found. Please check your data.")
        return None

    start_period = pd.Timestamp(start_period).tz_localize('UTC')
    end_period = pd.Timestamp(end_period).tz_localize('UTC')
    mask = (place_visits['start_datetime'] >= start_period) & (place_visits['start_datetime'] <= end_period)
    place_visits = place_visits.loc[mask].reset_index(drop=True)
    print(f"Place visits after date filtering: {len(place_visits)}")

    if place_visits.empty:
        print("No place visits found in the specified time range.")
        return None

    place_visits['day_of_week'] = place_visits['start_datetime'].dt.day_name()
    place_visits['start_hour'] = place_visits['start_datetime'].dt.hour

    return place_visits
