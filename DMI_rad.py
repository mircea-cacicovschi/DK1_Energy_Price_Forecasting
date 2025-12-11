from dmi_open_data import DMIOpenDataClient
from datetime import datetime
import pandas as pd

# Load DK1 stations
df_stations = pd.read_csv("dk1_stations_final.csv", dtype={"stationId": str})

# Initialize DMI API
KEY = "6a73aa34-dc49-49d7-af91-5b8d487edf9f"
client = DMIOpenDataClient(api_key=KEY)

all_station_daily = []

for _, row in df_stations.iterrows():
    station_id = row["stationId"].zfill(5)
    station_name = row["name"]
    print(f"Fetching global radiation for: {station_name} (Station ID: {station_id})")

    try:
        df_rad = client.get_observations(
            parameter="radia_glob_past1h",
            station_id=station_id,
            from_time=datetime(2015, 1, 1),
            to_time=datetime(2025, 8, 1),
            limit=300000,
            offset=1,
            as_df=True
        )

        if df_rad.empty or "observed" not in df_rad.columns or "value" not in df_rad.columns:
            print("  No data or missing columns. Skipping.")
            continue

        df_rad["observed"] = pd.to_datetime(df_rad["observed"])
        df_rad.set_index("observed", inplace=True)

        # Daily total radiation in J/m²
        df_daily_rad = df_rad["value"].resample("D").sum().rename(station_name)
        all_station_daily.append(df_daily_rad)

    except Exception as e:
        print(f"  Failed to fetch data: {e}")
        continue

# Combine all stations and average per day
df_combined = pd.concat(all_station_daily, axis=1)
df_combined["DK1 average global radiation"] = df_combined.mean(axis=1)

# Prepare for export
df_result = df_combined[["DK1 average global radiation"]].reset_index()
df_result.rename(columns={"observed": "Date"}, inplace=True)
df_result["Date"] = df_result["Date"].dt.date

# Export
df_result.to_csv("dk1_daily_avg_radiation.csv", index=False)
print("Saved DK1 daily average global radiation to 'dk1_daily_avg_radiation.csv'")