import pandas as pd
from collections import Counter

def truncate_name(name, max_length=10):
    if pd.isnull(name) or not isinstance(name, str):
        return None
    return name[:max_length]

def create_weekly_schedule(place_visits, max_name_length=10):
    place_visits['place_name_truncated'] = place_visits['place_name'].apply(
        lambda x: truncate_name(x, max_name_length)
    )

    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = range(24)

    schedule_df = pd.DataFrame(index=hours, columns=days_order)

    hourly_location_frequencies = {}

    for hour in hours:
        hour_visits = place_visits[place_visits['start_hour'] == hour]
        valid_visits = hour_visits[hour_visits['place_name_truncated'].notnull()]
        places = valid_visits['place_name_truncated']
        freq = Counter(places)
        sorted_places = [place for place, count in freq.most_common()]
        hourly_location_frequencies[hour] = sorted_places

    #create schedule
    for day in days_order:
        for hour in hours:
            mask = (
                (place_visits['day_of_week'] == day) &
                (place_visits['start_hour'] == hour)
            )
            visits = place_visits.loc[mask]

            if not visits.empty:
                valid_visits = visits[visits['place_name_truncated'].notnull()]

                if not valid_visits.empty:
                    most_common_place = valid_visits['place_name_truncated'].mode().iloc[0]
                    schedule_df.at[hour, day] = most_common_place
                else:
                    schedule_df.at[hour, day] = None
            else:
                places_at_hour = hourly_location_frequencies.get(hour, [])
                if places_at_hour:
                    schedule_df.at[hour, day] = places_at_hour[0]
                else:
                    schedule_df.at[hour, day] = None

    return schedule_df
