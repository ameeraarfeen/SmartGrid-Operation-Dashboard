import pandas as pd

df = pd.read_parquet("ukpn-smart-meter-consumption-substation.parquet")
df["t"] = df["data_collection_log_timestamp"].dt.tz_convert("Europe/London")
df = df.dropna(subset=["total_consumption_active_import"])

start = pd.Timestamp("2026-08-03", tz="Europe/London")
end = pd.Timestamp("2026-08-17", tz="Europe/London")
df = df[(df["t"] >= start) & (df["t"] < end)]
times = pd.date_range(start, periods=672, freq="30min")

cnt = df.pivot(index="t", columns="secondary_substation_id",
               values="aggregated_device_count_active").reindex(times)
rate = cnt / cnt.max()
feeder_rate = cnt.sum(axis=1) / cnt.max().sum()

print(cnt.max().describe())
print("Mean success (%):", round(100 * feeder_rate.mean(), 1))
print("Worst slot (%):", round(100 * feeder_rate.min(), 1), feeder_rate.idxmin())
print("Time below 95% (%):", round(100 * (feeder_rate < 0.95).mean(), 1))
print(rate.mean().sort_values().head(3))

feeder_rate.to_csv("comm_success.csv")