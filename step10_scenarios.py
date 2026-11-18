import numpy as np
import pandas as pd
import pandapower as pp
import pandapower.networks as pn

bus_shape = np.load("bus_shape.npy")
times = pd.date_range("2026-08-03", periods=672, freq="30min", tz="Europe/London")

def run(scale):
    net = pn.case33bw()
    base_p = net.load.p_mw.values.copy()
    base_q = net.load.q_mvar.values.copy()
    rows = []
    for k in range(len(times)):
        net.load["p_mw"] = base_p * bus_shape[k] * scale
        net.load["q_mvar"] = base_q * bus_shape[k] * scale
        pp.runpp(net, numba=False)
        v = net.res_bus.vm_pu
        rows.append((v.min(), (v < 0.95).sum()))
    out = pd.DataFrame(rows, columns=["min_v", "n_below"], index=times)
    out["compliance"] = 100 * (33 - out["n_below"]) / 33
    return out

for scale in [1.0, 1.55]:
    r = run(scale)
    r.to_csv(f"results_scale_{scale}.csv")
    print("scale", scale)
    print("  lowest voltage:", round(r.min_v.min(), 3))
    print("  worst compliance (%):", round(r.compliance.min(), 1))
    print("  time with any violation (%):", round(100 * (r.n_below > 0).mean(), 1))
    print("  worst slot:", r.compliance.idxmin())