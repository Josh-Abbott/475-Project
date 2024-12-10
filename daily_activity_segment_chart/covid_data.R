library(RSQLite)
library(dplyr)
library(lubridate)
library(ggplot2)
library(here)

#location of sql database file
db_path <- here("location_data.db")

con <- dbConnect(RSQLite::SQLite(), db_path)
activity_segments <- dbGetQuery(con, "SELECT * FROM activity_segments")
place_visits <- dbGetQuery(con, "SELECT * FROM place_visits")
dbDisconnect(con)


#convert timestamps to POSIXct date-time objects and calculate duration
activity_segments <- activity_segments %>%
  mutate(
    start_timestamp = sub("Z$", "", start_timestamp),
    end_timestamp = sub("Z$", "", end_timestamp),
    start_timestamp = ymd_hms(start_timestamp, tz = "UTC"),
    end_timestamp = ymd_hms(end_timestamp, tz = "UTC"),
    duration = as.numeric(difftime(end_timestamp, start_timestamp, units = "mins"))
  )

place_visits <- place_visits %>%
  mutate(
    start_timestamp = sub("Z$", "", start_timestamp),
    end_timestamp = sub("Z$", "", end_timestamp),
    start_timestamp = ymd_hms(start_timestamp, tz = "UTC"),
    end_timestamp = ymd_hms(end_timestamp, tz = "UTC"),
    duration = as.numeric(difftime(end_timestamp, start_timestamp, units = "mins"))
  )

# convert timestamps to date objects
activity_segments <- activity_segments %>%
  mutate(date = as.Date(start_timestamp))

#missing lat data
activity_segments <- activity_segments %>%
  filter(!is.na(start_latitude) & !is.na(start_longitude))

#missing long data
place_visits <- place_visits %>%
  filter(!is.na(latitude) & !is.na(longitude))

#summary statistics

summary(activity_segments$duration)
summary(activity_segments$distance_meters)

summary(place_visits$duration)

table(activity_segments$travel_mode)

length(unique(place_visits$place_name))

#split by time for comparisons
activity_segments <- activity_segments %>%
  mutate(
    period = case_when(
      date < as.Date("2020-03-01") ~ "Pre-Pandemic",
      date >= as.Date("2020-03-01") ~ "Pandemic"
    )
  )

activity_count <- activity_segments %>%
  group_by(period, date) %>%
  summarize(count = n(), .groups = 'drop')

# activity frequency comparison

ggplot(activity_count, aes(x = date, y = count, color = period)) +
  geom_line() +
  labs(title = "Activity Frequency Before and During Pandemic",
       x = "Date", y = "Number of Activities") +
  theme_minimal()

#travel mode usage comparison

distance_analysis <- activity_segments %>%
  group_by(period) %>%
  summarize(
    avg_distance = mean(distance_meters, na.rm = TRUE),
    median_distance = median(distance_meters, na.rm = TRUE),
    .groups = 'drop'
  )

#filter data to make more accurate bar graph

travel_mode_analysis <- activity_segments %>%
  filter(!is.na(travel_mode)) %>%
  group_by(period, travel_mode) %>%
  summarize(count = n(), .groups = 'drop') %>%
  filter(count > 5)  # Remove travel modes with count of 5

ggplot(travel_mode_analysis, aes(x = travel_mode, y = count, fill = period)) +
  geom_bar(stat = "identity", position = "dodge") +
  labs(title = "Travel Mode Usage Before & During Pandemic",
       x = "Travel Mode", y = "Count") +
  theme_minimal()

#activity density comparison (heatmap)

activity_segments <- activity_segments %>%
  mutate(
    day_of_week = wday(date, label = TRUE),
    hour = hour(as.POSIXct(start_timestamp))
  )

heatmap_data <- activity_segments %>%
  group_by(period, day_of_week, hour) %>%
  summarize(activity_count = n(), .groups = 'drop')

ggplot(heatmap_data, aes(x = hour, y = day_of_week, fill = activity_count)) +
  geom_tile() +
  facet_wrap(~ period) +
  scale_fill_gradient(low = "lightblue", high = "darkblue") +
  labs(
    title = "Activity Density by Day and Hour",
    x = "Hour of Day", y = "Day of Week", fill = "Activity Count"
  ) +
  theme_minimal()

