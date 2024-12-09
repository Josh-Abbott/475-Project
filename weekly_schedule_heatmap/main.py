from data_loader import load_data
from weekly_schedule import create_weekly_schedule
from visualize_schedule import visualize_schedule

folder_path = 'data'

start_period = '2019-01-01'
end_period = '2019-06-30'

place_visits = load_data(
    folder_path=folder_path,
    start_period=start_period,
    end_period=end_period
)

if place_visits is not None:
    max_name_length = 10
    schedule_df = create_weekly_schedule(place_visits, max_name_length=max_name_length)

    print("Weekly Schedule:")
    print(schedule_df)

    visualize_schedule(
        schedule_df,
        wrap_width=10,
        start_period=start_period,
        end_period=end_period
    )
else:
    print("No data available to create a schedule.")
