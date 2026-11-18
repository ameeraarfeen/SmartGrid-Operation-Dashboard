import numpy as np
import pandas as pd
import pandapower as pp
import pandapower.networks as pn
import matplotlib.pyplot as plt

bus_shape = np.load("bus_shape.npy")
pv_mw = np.load("pv_mw.npy") * 3
times = pd.date_range("2026-08-03", periods=672, freq="30min", tz="Europe/London")
pv_buses = [8, 14, 17, 24, 32]

BESS_BUS, P_MAX, EFF, DT = 17, 0.5, 0.95, 0.5

def run(e_mwh):
    net = pn.case33bw()
    base_p = net.load.p_mw.values.copy()
    base_q = net.load.q_mvar.values.copy()
    for b in pv_buses:
        pp.create_sgen(net, bus=b, p_mw=0.0, q_mvar=0.0)
    if e_mwh > 0:
        pp.create_storage(net, bus=BESS_BUS, p_mw=0.0, max_e_mwh=e_mwh)
    soc = 0.2 * e_mwh
    rows = []
    for k in range(len(times)):
        net.load["p_mw"] = base_p * bus_shape[k]
        net.load["q_mvar"] = base_q * bus_shape[k]
        net.sgen["p_mw"] = pv_mw[k]
        p_batt = 0.0
        if e_mwh > 0:
            net.storage["p_mw"] = 0.0
            pp.runpp(net, numba=False)
            vmax = net.res_bus.vm_pu.max()
            vmin = net.res_bus.vm_pu.min()
            if vmax > 1.03 and soc < 0.9 * e_mwh:
                p_batt = min(P_MAX, (0.9 * e_mwh - soc) / (EFF * DT))
                soc += p_batt * EFF * DT
            elif vmin < 0.955 and soc > 0.1 * e_mwh:
                p_dis = min(P_MAX, (soc - 0.1 * e_mwh) * EFF / DT)
                soc -= p_dis * DT / EFF
                p_batt = -p_dis
            net.storage["p_mw"] = p_batt
        pp.runpp(net, numba=False)
        v = net.res_bus.vm_pu
        rows.append((v.min(), v.max(), (v < 0.95).sum(), (v > 1.05).sum(),
                     net.res_ext_grid.p_mw.iloc[0], p_batt, soc))
    return pd.DataFrame(rows, index=times, columns=[
        "min_v", "max_v", "n_low", "n_high", "grid_mw", "batt_mw", "soc_mwh"])

fig, ax = plt.subplots(2, 1, sharex=True)
for e in [0, 2, 4]:
    r = run(e)
    r.to_csv(f"results_bess_{e}mwh.csv")
    print("Battery", e, "MWh")
    print("  time any bus below 0.95 (%):", round(100 * (r.n_low > 0).mean(), 1))
    print("  time any bus above 1.05 (%):", round(100 * (r.n_high > 0).mean(), 1))
    print("  time with reverse flow (%):", round(100 * (r.grid_mw < 0).mean(), 1))
    print("  highest voltage:", round(r.max_v.max(), 3), "| lowest:", round(r.min_v.min(), 3))
    h = r.index.hour
    ax[0].plot(r.groupby(h).max_v.mean(), label=f"{e} MWh")
    ax[1].plot(r.groupby(h).min_v.mean(), label=f"{e} MWh")
ax[0].axhline(1.05, color="red", linestyle="--")
ax[1].axhline(0.95, color="red", linestyle="--")
ax[0].set_ylabel("Avg highest V (pu)")
ax[1].set_ylabel("Avg lowest V (pu)")
ax[1].set_xlabel("Hour of day")
ax[0].legend()
plt.show()