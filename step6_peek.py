import pandas as pd

df = pd.read_parquet("ukpn-smart-meter-consumption-substation.parquet")
df["t"] = df["data_collection_log_timestamp"].dt.tz_convert("Europe/London")

print(df.shape)
print(df["secondary_substation_id"].nunique())
print(df["t"].min(), df["t"].max())