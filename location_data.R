library(RSQLite)
library(dplyr)
library(lubridate)
library(ggplot2)

#change to location of sql database file
db_path <- "C:\\Users\\Documents\\Repos\\475 project\\location_data.db"

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

#table(activity_segments$confidence)
#table(place_visits$visit_confidence)

length(unique(place_visits$place_name))

#travel mode bar chart (TODO: handle NA  travel_mode)
ggplot(activity_segments, aes(x = travel_mode)) +
  geom_bar(fill = "blue") +
  labs(title = "Frequency of Travel Modes", x = "Travel Mode", y = "Count")

#activities per day
daily_activities <- activity_segments %>%
  mutate(date = as.Date(start_timestamp)) %>%
  group_by(date) %>%
  summarize(count = n())

#activities per day plot
ggplot(daily_activities, aes(x = date, y = count)) +
  geom_line(color = "blue") +
  labs(title = "Daily Activity Segments", x = "Date", y = "Number of Activities")


library(leaflet)

#map of places visited
leaflet(place_visits) %>%
  addTiles() %>%
  addCircleMarkers(
    lng = ~longitude, lat = ~latitude,
    radius = 5,
    popup = ~place_name,
    color = "red",
    stroke = FALSE, fillOpacity = 0.5
  ) %>%
  addLegend("bottomright", colors = "red", labels = "Place Visits")


set.seed(123)
coordinates <- place_visits %>%
  select(longitude, latitude)

clusters <- kmeans(coordinates, centers = 5)
place_visits$cluster <- as.factor(clusters$cluster)

#map cluster?
leaflet(place_visits) %>%
  addTiles() %>%
  addCircleMarkers(
    lng = ~longitude, lat = ~latitude,
    color = ~cluster,
    popup = ~place_name,
    stroke = FALSE, fillOpacity = 0.5
  )





