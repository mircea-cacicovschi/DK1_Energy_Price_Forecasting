import pandas as pd
import requests
import time
from tqdm import tqdm

# Load stations
stations = pd.read_csv("dk1_stations_forcast_vars.csv")

# Forecast variables
variables = [
    "temperature_2m", "precipitation", "wind_speed_10m",
    "relative_humidity_2m", "cloudcover", "shortwave_radiation"
]

# API setup
BASE_URL = "https://api.open-meteo.com/v1/forecast"
params_template = {
    "hourly": ",".join(variables),
    "wind_speed_unit": "ms",
    "forecast_days": 14,
    "timezone": "auto"
}

# Storage
all_forecasts = []

# Loop over stations
for _, row in tqdm(stations.iterrows(), total=len(stations), desc="Fetching station forecasts"):
    lat = row['latitude']
    lon = row['longitude']
    station_id = row['stationId']
    station_name = row['name']

    params = params_template.copy()
    params.update({"latitude": lat, "longitude": lon})

    success = False
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            hourly = response.json()["hourly"]

            df = pd.DataFrame({"datetime": hourly["time"]})
            for var in variables:
                df[var] = hourly.get(var, [None] * len(df))
            df["stationId"] = station_id
            df["station_name"] = station_name
            all_forecasts.append(df)
            success = True
            break
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {station_name}: {e}")
            time.sleep(3)

    if not success:
        print(f"⚠️ Failed to fetch data for {station_name} after {retries} attempts.")

# Combine and save
forecast_df = pd.concat(all_forecasts, ignore_index=True)
forecast_df.to_csv("dk1_forecast_14d.csv", index=False)
print("Forecasts saved to dk1_forecast_14d.csv")

# Load the combined hourly forecast data from all stations
df = pd.read_csv("dk1_forecast_14d.csv") 

# Convert to datetime
df["time"] = pd.to_datetime(df["datetime"])
df["Date"] = df["time"].dt.date

# List of columns to average or sum
avg_vars = ["temperature_2m", "wind_speed_10m", "relative_humidity_2m", "cloudcover"]
sum_vars = ["shortwave_radiation", "precipitation"]

# Step 1: Aggregate hourly → daily per station
daily_station = df.groupby(["stationId", "Date"]).agg({
    **{var: "mean" for var in avg_vars},
    **{var: "sum" for var in sum_vars}
}).reset_index()

# Step 2: Average across stations to create DK1 regional daily forecast
daily_station_clean = daily_station.drop(columns="stationId")
dk1_daily = daily_station_clean.groupby("Date").agg("mean").reset_index()

# Optional: save result
dk1_daily.to_csv("dk1_daily_forecast.csv", index=False)

# Show preview
print(dk1_daily.head())


