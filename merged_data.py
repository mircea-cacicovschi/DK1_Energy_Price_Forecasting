import pandas as pd

# Load all CSV files
df_price = pd.read_csv("entsoe_daily_prices_DK1.csv")
df_temp = pd.read_csv("dk1_daily_avg_temperature.csv")
df_precip = pd.read_csv("dk1_daily_avg_precipitation.csv")
df_wind = pd.read_csv("dk1_daily_avg_wind_speed.csv")
df_humidity = pd.read_csv("dk1_daily_avg_humidity.csv")
df_cloud = pd.read_csv("dk1_daily_avg_cloud_cover.csv")
df_radiation = pd.read_csv("dk1_daily_avg_radiation.csv")

# Standardize date column
for df in [df_price, df_temp, df_precip, df_wind, df_humidity, df_cloud, df_radiation]:
    df.rename(columns={df.columns[0]: "Date"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])

# Merge all dataframes on "Date"
df_merged = df_price.merge(df_temp, on="Date", how="inner") \
                    .merge(df_precip, on="Date", how="inner") \
                    .merge(df_wind, on="Date", how="inner") \
                    .merge(df_humidity, on="Date", how="inner") \
                    .merge(df_cloud, on="Date", how="inner") \
                    .merge(df_radiation, on="Date", how="inner")

# Rename columns for clarity
df_merged.columns = [
    "Date",
    "Price (EUR/MWh)",
    "DK1 average temperature",
    "DK1 average precipitation",
    "DK1 average wind speed",
    "DK1 average humidity (%)",
    "DK1 average cloud cover (%)",
    "DK1 average global radiation"
]

# Add date-related features
df_merged["Weekday"] = df_merged["Date"].dt.weekday       # 0 = Monday, 6 = Sunday
df_merged["Month"] = df_merged["Date"].dt.month           # 1 = January, 12 = December
df_merged["DayOfMonth"] = df_merged["Date"].dt.day        # 1–31

# Export merged dataframe
df_merged.to_csv("merged_energy_weather_data.csv", index=False)