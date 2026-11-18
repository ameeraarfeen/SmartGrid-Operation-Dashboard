import numpy as np
import pandas as pd
import pandapower as pp
import pandapower.networks as pn
import matplotlib.pyplot as plt

bus_shape = np.load("bus_shape.npy")
pv_mw = np.load("pv_mw.npy")
times = pd.date_range("2026-08-03", periods=672, freq="30min", tz="Europe/London")
pv_buses = [8, 14, 17, 24, 32]

def run(scale, with_pv):
    net = pn.case33bw()
    base_p = net.load.p_mw.values.copy()
    base_q = net.load.q_mvar.values.copy()
    if with_pv:
        for b in pv_buses:
            pp.create_sgen(net, bus=b, p_mw=0.0, q_mvar=0.0)
    rows = []
    for k in range(len(times)):
        net.load["p_mw"] = base_p * bus_shape[k] * scale
        net.load["q_mvar"] = base_q * bus_shape[k] * scale
        if with_pv:
            net.sgen["p_mw"] = pv_mw[k]
        pp.runpp(net, numba=False)
        v = net.res_bus.vm_pu
        rows.append((v.min(), v.max(), (v < 0.95).sum(),
                     net.res_ext_grid.p_mw.iloc[0]))
    out = pd.DataFrame(rows, columns=["min_v", "max_v", "n_below", "grid_mw"],
                       index=times)
    out["compliance"] = 100 * (33 - out["n_below"]) / 33
    return out

results = {}
for scale in [1.0, 1.55]:
    for with_pv in [False, True]:
        r = run(scale, with_pv)
        results[(scale, with_pv)] = r
        r.to_csv(f"results_scale_{scale}_pv_{with_pv}.csv")
        hr = r.index.hour
        print("scale", scale, "| PV:", with_pv)
        print("  lowest voltage:", round(r.min_v.min(), 3))
        print("  highest voltage:", round(r.max_v.max(), 3))
        print("  worst compliance (%):", round(r.compliance.min(), 1))
        print("  time with any violation (%):", round(100 * (r.n_below > 0).mean(), 1))
        print("  violation share 10-15h (%):",
              round(100 * (r.n_below[(hr >= 10) & (hr < 15)] > 0).mean(), 1))
        print("  violation share 18-21h (%):",
              round(100 * (r.n_below[(hr >= 18) & (hr < 21)] > 0).mean(), 1))
        print("  lowest grid import (MW):", round(r.grid_mw.min(), 2))

for with_pv in [False, True]:
    r = results[(1.55, with_pv)]
    r.groupby(r.index.hour).min_v.mean().plot(label=f"PV: {with_pv}")
plt.axhline(0.95, color="red", linestyle="--")
plt.xlabel("Hour of day")
plt.ylabel("Average lowest voltage (pu), scale 1.55")
plt.legend()
plt.show()