import pandas as pd

df = pd.read_parquet("ukpn-smart-meter-consumption-substation.parquet")
df["t"] = df["data_collection_log_timestamp"].dt.tz_convert("Europe/London")

df = df.dropna(subset=["total_consumption_active_import"])
start = pd.Timestamp("2026-08-03", tz="Europe/London")
end = pd.Timestamp("2026-08-17", tz="Europe/London")
df = df[(df["t"] >= start) & (df["t"] < end)]

load = df.pivot(index="t", columns="secondary_substation_id",
                values="total_consumption_active_import")

times = pd.date_range(start, periods=672, freq="30min")
load = load.reindex(times)

print(load.shape)
print("Missing values:", load.isna().sum().sum())

import numpy as np
import pandapower.networks as pn
import matplotlib.pyplot as plt

net = pn.case33bw()
base_p = net.load.p_mw.values

shape = (load / load.max()).values
bus_shape = np.column_stack([shape[:, i % 18] for i in range(len(base_p))])
feeder_mw = (bus_shape * base_p).sum(axis=1)

print(bus_shape.shape)
print("Peak feeder load (MW):", feeder_mw.max())

pd.Series(feeder_mw, index=times).plot()
plt.ylabel("Feeder load (MW)")
plt.show()

np.save("bus_shape.npy", bus_shape)