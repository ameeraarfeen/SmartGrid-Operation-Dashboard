import numpy as np
import pandas as pd
import pandapower as pp
import pandapower.networks as pn
import matplotlib.pyplot as plt

bus_shape = np.load("bus_shape.npy")
times = pd.date_range("2026-08-03", periods=672, freq="30min", tz="Europe/London")

net = pn.case33bw()
base_p = net.load.p_mw.values.copy()
base_q = net.load.q_mvar.values.copy()
scale = 1.0

min_v = []
n_below = []
for k in range(len(times)):
    net.load["p_mw"] = base_p * bus_shape[k] * scale
    net.load["q_mvar"] = base_q * bus_shape[k] * scale
    pp.runpp(net, numba=False)
    v = net.res_bus.vm_pu
    min_v.append(v.min())
    n_below.append((v < 0.95).sum())

result = pd.DataFrame({"min_v": min_v, "n_below": n_below}, index=times)
result["compliance"] = 100 * (33 - result["n_below"]) / 33
print(result.describe())
result["compliance"].plot()
plt.ylabel("Voltage compliance (%)")
plt.show()