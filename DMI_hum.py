from dmi_open_data import DMIOpenDataClient
from datetime import datetime
import pandas as pd
import os

# Load DK1 station list
df_stations = pd.read_csv("dk1_stations_final.csv", dtype={"stationId": str})

# Initialize API client
KEY = os.getenv("DMI_API_KEY")
if KEY is None:
    raise RuntimeError(
        "DMI_API_KEY environment variable not set. "
        "Please set it before running this script."
    )
client = DMIOpenDataClient(api_key=KEY)

# Storage for daily humidity from each station
all_station_daily = []

# Loop over each station
for _, row in df_stations.iterrows():
    station_id = row["stationId"].zfill(5)
    station_name = row["name"]
    print(f"Fetching humidity for: {station_name} (Station ID: {station_id})")

    try:
        df_hum = client.get_observations(
            parameter="humidity_past1h",
            station_id=station_id,
            from_time=datetime(2015, 1, 1),
            to_time=datetime(2025, 8, 1),
            limit=300000,
            offset=1,
            as_df=True
        )

        if df_hum.empty or "observed" not in df_hum.columns or "value" not in df_hum.columns:
            print("  No data or missing columns. Skipping.")
            continue

        df_hum["observed"] = pd.to_datetime(df_hum["observed"])
        df_hum.set_index("observed", inplace=True)

        # Resample to daily average humidity (%)
        df_daily_hum = df_hum["value"].resample("D").mean().rename(station_name)
        all_station_daily.append(df_daily_hum)

    except Exception as e:
        print(f"  Failed to fetch data: {e}")
        continue

# Combine and compute DK1 daily average humidity
df_combined = pd.concat(all_station_daily, axis=1)
df_combined["DK1 average humidity (%)"] = df_combined.mean(axis=1)

# Format and export
df_result = df_combined[["DK1 average humidity (%)"]].reset_index()
df_result.rename(columns={"observed": "Date"}, inplace=True)
df_result["Date"] = df_result["Date"].dt.date

df_result.to_csv("dk1_daily_avg_humidity.csv", index=False)
print("\n✅ Saved DK1 daily average humidity to 'dk1_daily_avg_humidity.csv'")
