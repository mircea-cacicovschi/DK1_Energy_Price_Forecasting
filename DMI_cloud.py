from dmi_open_data import DMIOpenDataClient
from datetime import datetime
import pandas as pd
import os

# Load DK1 station list
df_stations = pd.read_csv("dk1_stations_final.csv", dtype={"stationId": str})

# Initialize DMI API
KEY = os.getenv("DMI_API_KEY")
if KEY is None:
    raise RuntimeError(
        "DMI_API_KEY environment variable not set. "
        "Please set it before running this script."
    )
client = DMIOpenDataClient(api_key=KEY)

# Map cloud cover codes to estimated % coverage
cloud_cover_mapping = {
    0: 0.0,
    10: 12.5,
    25: 25.0,
    40: 37.5,
    50: 50.0,
    60: 62.5,
    75: 75.0,
    90: 87.5,
    100: 100.0,
    112: None  # Sky obscured — treat as missing
}

# Generate list of yearly date chunks
date_ranges = [
    (datetime(year, 1, 1), datetime(year, 12, 31)) for year in range(2015, 2025)
]
date_ranges.append((datetime(2025, 1, 1), datetime(2025, 8, 1)))

# Storage for all stations' daily averages
all_station_daily = []

# Loop through stations
for _, row in df_stations.iterrows():
    station_id = row["stationId"].zfill(5)
    station_name = row["name"]
    print(f"\nFetching cloud cover for: {station_name} (Station ID: {station_id})")

    dfs = []

    # Loop through each yearly chunk
    for from_time, to_time in date_ranges:
        try:
            df_chunk = client.get_observations(
                parameter="cloud_cover",
                station_id=station_id,
                from_time=from_time,
                to_time=to_time,
                limit=300000,
                offset=1,
                as_df=True
            )

            if not df_chunk.empty and "observed" in df_chunk.columns and "value" in df_chunk.columns:
                dfs.append(df_chunk)

        except Exception as e:
            print(f"  Skipping range {from_time.date()} to {to_time.date()} — Error: {e}")
            continue

    if not dfs:
        print("  No data retrieved for this station.")
        continue

    # Combine yearly chunks
    df_cloud = pd.concat(dfs, ignore_index=True)
    df_cloud["observed"] = pd.to_datetime(df_cloud["observed"])
    df_cloud.set_index("observed", inplace=True)
    df_cloud["percent"] = df_cloud["value"].map(cloud_cover_mapping)

    # Resample to daily mean
    df_daily_cloud = df_cloud["percent"].resample("D").mean().rename(station_name)
    all_station_daily.append(df_daily_cloud)

# Combine and compute DK1-wide daily average
df_combined = pd.concat(all_station_daily, axis=1)
df_combined["DK1 average cloud cover (%)"] = df_combined.mean(axis=1)

# Format and export
df_result = df_combined[["DK1 average cloud cover (%)"]].reset_index()
df_result.rename(columns={"observed": "Date"}, inplace=True)
df_result["Date"] = df_result["Date"].dt.date

df_result.to_csv("dk1_daily_avg_cloud_cover.csv", index=False)
print("\n✅ Saved DK1 daily average cloud cover to 'dk1_daily_avg_cloud_cover.csv'")
