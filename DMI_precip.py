from dmi_open_data import DMIOpenDataClient
from datetime import datetime
import pandas as pd

# Load stations
df_stations = pd.read_csv("dk1_stations_final.csv", dtype={"stationId": str})

# API setup
KEY = "6a73aa34-dc49-49d7-af91-5b8d487edf9f"
client = DMIOpenDataClient(api_key=KEY)

# Prepare list of daily data
all_station_daily = []

for _, row in df_stations.iterrows():
    station_id = row["stationId"].zfill(5)
    station_name = row["name"]
    print(f"Fetching precipitation for: {station_name} (Station ID: {station_id})")

    try:
        df_precip = client.get_observations(
            parameter="precip_past1h",
            station_id=station_id,
            from_time=datetime(2015, 1, 1),
            to_time=datetime(2025, 8, 1),
            limit=300000,
            offset=1,
            as_df=True
        )

        if df_precip.empty or "observed" not in df_precip.columns or "value" not in df_precip.columns:
            print("  No data or missing columns. Skipping.")
            continue

        df_precip["observed"] = pd.to_datetime(df_precip["observed"])
        df_precip.set_index("observed", inplace=True)

        # Replace trace amount code -0.1 with estimated 0.05 mm
        df_precip["value"] = df_precip["value"].replace(-0.1, 0.05)

        # Daily total (not mean)
        df_daily_precip = df_precip["value"].resample("D").sum().rename(station_name)
        all_station_daily.append(df_daily_precip)

    except Exception as e:
        print(f"  Failed to fetch data: {e}")
        continue

# Combine and calculate DK1 average precipitation (daily mean across stations)
df_combined = pd.concat(all_station_daily, axis=1)
df_combined["DK1 average precipitation"] = df_combined.mean(axis=1)

# Format and save
df_result = df_combined[["DK1 average precipitation"]].reset_index()
df_result.rename(columns={"observed": "Date"}, inplace=True)
df_result["Date"] = df_result["Date"].dt.date

df_result.to_csv("dk1_daily_avg_precipitation.csv", index=False)
print("Saved DK1 daily average precipitation to 'dk1_daily_avg_precipitation.csv'")