import os
from dmi_open_data import DMIOpenDataClient, Parameter
from datetime import datetime
import pandas as pd

# Read DMI API key from environment
KEY = os.getenv("DMI_API_KEY")
if KEY is None:
    raise RuntimeError(
        "DMI_API_KEY environment variable not set. "
        "Please set it before running this script."
    )

client = DMIOpenDataClient(api_key=KEY)

# Example: Aarhus DMI station (or use client.get_closest_station())
station_id = "06120"

# Get temperature data as a clean DataFrame
df_temp = client.get_observations(
    parameter="cloud_cover",
    station_id=station_id,
    from_time=datetime(2015, 1, 1),
    to_time=datetime(2025, 6, 1),
    limit = 300000,
    offset= 1,
    as_df=True 
)

df_temp.to_csv("checking.csv", index=False)
df_temp.sort_values(by="observed", inplace=True)
df_temp.reset_index(drop=True, inplace=True) 

df_temp["observed"] = pd.to_datetime(df_temp["observed"])
df_temp.set_index("observed", inplace=True)

df_daily_temp = df_temp["value"].resample("D").mean()

df_avg_temp = df_daily_temp.reset_index()  # Moves the datetime index back to a column
df_avg_temp["Date"] = df_avg_temp["observed"].dt.date  # Strip time (keep YYYY-MM-DD)
df_avg_temp.rename(columns={"value": "value"}, inplace=True)
df_avg_temp = df_avg_temp[["Date", "value"]]  # Reorder columns
print(df_avg_temp.head(5))
