import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

times = pd.date_range("2026-08-03", periods=672, freq="30min", tz="Europe/London")

sun = pd.read_csv("irradiance_london.csv", parse_dates=["time"])
s = sun.set_index("time")["ghi_wm2"]
s.index = s.index.tz_localize("Europe/London")
ghi30 = s.reindex(times).interpolate().ffill()

pv_buses = [8, 14, 17, 24, 32]
cap_mw = 0.3
pv_per_mw = 0.8 * ghi30.values / 1000
pv_mw = np.outer(pv_per_mw, np.full(len(pv_buses), cap_mw))

np.save("pv_mw.npy", pv_mw)
print(pv_mw.shape)
print("Peak total PV (MW):", pv_mw.sum(axis=1).max())

pd.Series(pv_mw.sum(axis=1), index=times).plot()
plt.ylabel("Total PV output (MW)")
plt.show()