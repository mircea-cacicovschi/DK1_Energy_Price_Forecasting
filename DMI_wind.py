from dmi_open_data import DMIOpenDataClient
from datetime import datetime
import pandas as pd

# Load station list
df_stations = pd.read_csv("dk1_stations_final.csv", dtype={"stationId": str})

# Initialize DMI API
KEY = "6a73aa34-dc49-49d7-af91-5b8d487edf9f"
client = DMIOpenDataClient(api_key=KEY)

# Container for each station's daily wind speed
all_station_daily = []

# Loop over stations
for _, row in df_stations.iterrows():
    station_id = row["stationId"].zfill(5)
    station_name = row["name"]
    print(f"Fetching wind data for: {station_name} (Station ID: {station_id})")

    try:
        df_wind = client.get_observations(
            parameter="wind_speed_past1h",
            station_id=station_id,
            from_time=datetime(2015, 1, 1),
            to_time=datetime(2025, 8, 1),
            limit=300000,
            offset=1,
            as_df=True
        )

        if df_wind.empty or "observed" not in df_wind.columns or "value" not in df_wind.columns:
            print("  No data or missing columns. Skipping.")
            continue

        df_wind["observed"] = pd.to_datetime(df_wind["observed"])
        df_wind.set_index("observed", inplace=True)
        df_daily_wind = df_wind["value"].resample("D").mean().rename(station_name)

        all_station_daily.append(df_daily_wind)

    except Exception as e:
        print(f"  Failed to fetch data: {e}")
        continue

# Combine all stations and calculate DK1 average wind speed
df_combined = pd.concat(all_station_daily, axis=1)
df_combined["DK1 average wind speed"] = df_combined.mean(axis=1)

# Format for export
df_result = df_combined[["DK1 average wind speed"]].reset_index()
df_result.rename(columns={"observed": "Date"}, inplace=True)
df_result["Date"] = df_result["Date"].dt.date

# Export to CSV
df_result.to_csv("dk1_daily_avg_wind_speed.csv", index=False)
print("Saved DK1 daily average wind speeds to 'dk1_daily_avg_wind_speed.csv'")