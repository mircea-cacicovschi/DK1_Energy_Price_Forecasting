import os 
import requests
import pandas as pd
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET

# Read ENTSO-E token from environment
TOKEN = os.getenv("ENTSOE_API_KEY")

if TOKEN is None:
    raise RuntimeError(
        "ENTSOE_API_KEY environment variable not set. "
        "Please set it before running this script."
    )
    
area = '10YDK-1--------W'  # DK1: Western Denmark
document_type = 'A44'      # Day-ahead prices
process_type = 'A01'       # Realised

# --- Only this window ---
start_date = datetime(2025, 8, 1)   # inclusive
end_date   = datetime(2025, 8, 15)  # exclusive (to include Aug 14)
# ------------------------

data = []

current_date = start_date
while current_date < end_date:
    # Request in chunks (<=30 days); here it will be just one chunk
    chunk_end = min(current_date + timedelta(days=30), end_date)

    period_start = current_date.strftime('%Y%m%d%H%M')
    period_end = chunk_end.strftime('%Y%m%d%H%M')

    url = (
        "https://web-api.tp.entsoe.eu/api?"
        f"securityToken={TOKEN}"
        f"&documentType={document_type}"
        f"&processType={process_type}"
        f"&in_Domain={area}"
        f"&out_Domain={area}"
        f"&periodStart={period_start}"
        f"&periodEnd={period_end}"
    )

    print(f"Fetching: {period_start} to {period_end}")
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Request failed for {period_start} – skipping...")
        current_date = chunk_end
        continue

    root = ET.fromstring(response.content)

    for timeseries in root.findall(".//{*}TimeSeries"):
        for period in timeseries.findall(".//{*}Period"):
            start_time_str = period.find(".//{*}timeInterval/{*}start").text
            # Parse as UTC
            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%MZ")
            for point in period.findall(".//{*}Point"):
                position = int(point.find(".//{*}position").text) - 1
                price = float(point.find(".//{*}price.amount").text)
                timestamp = start_time + timedelta(hours=position)
                data.append({"Datetime (UTC)": timestamp, "Price (EUR/MWh)": price})

    current_date = chunk_end

# Build DataFrame
df = pd.DataFrame(data)

if df.empty:
    print("No data returned for the specified window.")
else:
    # Filter strictly to Aug 1, 2025 00:00 UTC up to (but not including) Aug 15, 2025 00:00 UTC
    df['Datetime (UTC)'] = pd.to_datetime(df['Datetime (UTC)'], utc=True)
    mask = (df['Datetime (UTC)'] >= pd.Timestamp('2025-08-01T00:00Z')) & \
           (df['Datetime (UTC)'] <  pd.Timestamp('2025-08-15T00:00Z'))
    df = df.loc[mask].copy()

    # Aggregate to daily (UTC calendar day)
    df['Date'] = df['Datetime (UTC)'].dt.date
    daily_df = df.groupby('Date', as_index=False)['Price (EUR/MWh)'].mean()

    # Export
    daily_df.to_csv("actual_aug.csv", index=False)
