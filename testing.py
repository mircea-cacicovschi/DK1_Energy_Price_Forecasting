import os 
from dmi_open_data import DMIOpenDataClient
import pandas as pd

# Initialize DMI API client using environment variable
KEY = os.getenv("DMI_API_KEY")
if KEY is None:
    raise RuntimeError(
        "DMI_API_KEY environment variable not set. "
        "Please set it before running this script."
    )

client = DMIOpenDataClient(api_key=KEY)

# Get all stations (GeoJSON-style structure)
stations = client.get_stations()

# Combine 'properties' and 'geometry.coordinates' into one flat dictionary per station
stations_flat = [{
    **s["properties"],
    "latitude": s["geometry"]["coordinates"][1],
    "longitude": s["geometry"]["coordinates"][0]
} for s in stations]

# Convert to DataFrame
df_stations = pd.DataFrame(stations_flat)
# print("Available station types:", df_stations["type"].unique())
# print("Available statuses:", df_stations["status"].unique())
# print("Available countries:", df_stations["country"].unique())

# Filter for Denmark, active, synop stations
df_dk_stations = df_stations[
    (df_stations["country"] == "DNK") &
    (df_stations["type"] == "Synop") &
    (df_stations["status"] == "Active")
]

print(df_dk_stations[["stationId", "name", "latitude", "longitude"]])

df_dk1_stations = df_dk_stations[df_dk_stations["longitude"] < 12.1]
print(df_dk1_stations[["stationId", "name", "latitude", "longitude"]])

df_dk1_cleaned = df_dk1_stations.drop_duplicates(subset=["stationId", "name"]).copy()

df_dk1_cleaned["map_link"] = "https://www.google.com/maps?q=" + df_dk1_cleaned["latitude"].astype(str) + "," + df_dk1_cleaned["longitude"].astype(str)
print(df_dk1_cleaned[["stationId", "name", "latitude", "longitude"]])

df_dk1_cleaned[["stationId", "name", "latitude", "longitude", "map_link"]].to_csv("dk1_stations.csv", index=False, encoding="utf-8")

stations_to_remove = ['06154', '06018', '06138', '06169', '06159', '06136', '06151', '06135', '06141', '06149', '06156', '06023', '06156']
df_dk1_final = df_dk1_cleaned[~df_dk1_cleaned["stationId"].isin(stations_to_remove)].copy()

df_dk1_final[["stationId", "name"]].to_csv("dk1_stations_final.csv", index=False, encoding="utf-8")

