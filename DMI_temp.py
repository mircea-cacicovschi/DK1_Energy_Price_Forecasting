from dmi_open_data import DMIOpenDataClient, Parameter
from datetime import datetime
import pandas as pd

# Load your curated DK1 stations list
df_stations = pd.read_csv("dk1_stations_final.csv")

# Initialize the API client
KEY = "6a73aa34-dc49-49d7-af91-5b8d487edf9f"
client = DMIOpenDataClient(api_key=KEY)

# Prepare to collect daily temperature data per station
all_station_daily = []

# Loop over each station
for _, row in df_stations.iterrows():
    station_id = str(row["stationId"]).zfill(5)
    station_name = row["name"]
    print(f"Fetching data for: {station_name} (Station ID: {station_id})")

    try:
        df_temp = client.get_observations(
            parameter="temp_mean_past1h",
            station_id=station_id,
            from_time=datetime(2015, 1, 1),
            to_time=datetime(2025, 8, 1),
            limit=300000,
            offset=1,
            as_df=True
        )

        if df_temp.empty or "observed" not in df_temp.columns or "value" not in df_temp.columns:
            print("  No data or missing columns. Skipping.")
            continue

        df_temp["observed"] = pd.to_datetime(df_temp["observed"])
        df_temp.set_index("observed", inplace=True)

        # Resample to daily mean and rename column
        df_daily = df_temp["value"].resample("D").mean().rename(station_name)
        all_station_daily.append(df_daily)

    except Exception as e:
        print(f"  Error: {e}")
        continue

# Combine all stations' daily means into one DataFrame
df_combined = pd.concat(all_station_daily, axis=1)

# Compute DK1-wide average temperature for each day
df_combined["DK1 average temperature"] = df_combined.mean(axis=1)

# Format for export
df_result = df_combined[["DK1 average temperature"]].reset_index()
df_result.rename(columns={"observed": "Date"}, inplace=True)
df_result["Date"] = df_result["Date"].dt.date

# Export to CSV
df_result.to_csv("dk1_daily_avg_temperature.csv", index=False)
print("Saved DK1 daily average temperatures to 'dk1_daily_avg_temperature.csv'")