import numpy as np
import pandas as pd
import pandapower as pp
import pandapower.networks as pn

bus_shape = np.load("bus_shape.npy")
pv_mw = np.load("pv_mw.npy")
times = pd.date_range("2026-08-03", periods=672, freq="30min", tz="Europe/London")
pv_buses = [8, 14, 17, 24, 32]

def run(pv_mult):
    net = pn.case33bw()
    base_p = net.load.p_mw.values.copy()
    base_q = net.load.q_mvar.values.copy()
    for b in pv_buses:
        pp.create_sgen(net, bus=b, p_mw=0.0, q_mvar=0.0)
    rows = []
    for k in range(len(times)):
        net.load["p_mw"] = base_p * bus_shape[k]
        net.load["q_mvar"] = base_q * bus_shape[k]
        net.sgen["p_mw"] = pv_mw[k] * pv_mult
        pp.runpp(net, numba=False)
        rows.append((net.res_bus.vm_pu.max(), net.res_ext_grid.p_mw.iloc[0]))
    return pd.DataFrame(rows, columns=["max_v", "grid_mw"], index=times)

for mult in [1, 2, 3, 4]:
    r = run(mult)
    print("PV peak (MW):", round(mult * pv_mw.sum(axis=1).max(), 1))
    print("  highest voltage:", round(r.max_v.max(), 3))
    print("  time with reverse flow (%):", round(100 * (r.grid_mw < 0).mean(), 1))
    print("  time any bus above 1.0 pu (%):", round(100 * (r.max_v > 1.0001).mean(), 1))