import numpy as np
import pandas as pd
import pandapower.networks as pn

times = pd.date_range("2026-08-03", periods=672, freq="30min", tz="Europe/London")
base_p = pn.case33bw().load.p_mw.values
bus_shape = np.load("bus_shape.npy")
pv = np.load("pv_mw.npy") * 3

bess = pd.read_csv("results_bess_2mwh.csv", index_col=0)
out = pd.read_csv("customers_out.csv", index_col=0).iloc[:, 0]
comm = pd.read_csv("comm_success.csv", index_col=0).iloc[:, 0]

m = pd.DataFrame(index=times)
m["load_mw"] = (bus_shape * base_p).sum(axis=1)
m["pv_mw"] = pv.sum(axis=1)
m["batt_mw"] = bess["batt_mw"].values
m["soc_mwh"] = bess["soc_mwh"].values
m["grid_mw"] = bess["grid_mw"].values
m["min_v"] = bess["min_v"].values
m["max_v"] = bess["max_v"].values
bad = bess["n_low"].values + bess["n_high"].values
m["voltage_compliance_pct"] = 100 * (33 - bad) / 33
m["pv_penetration_pct"] = 100 * m["pv_mw"] / m["load_mw"]
m["substation_loading_pct"] = 100 * m["grid_mw"] / 3.715
m["customers_out"] = out.values
m["comm_success_pct"] = 100 * comm.values

m["voltage_status"] = np.select(
    [(m.min_v < 0.94) | (m.max_v > 1.06), (m.min_v < 0.95) | (m.max_v > 1.05)],
    ["red", "amber"], "green")
m["comm_status"] = np.select(
    [m.comm_success_pct < 95, m.comm_success_pct < 98], ["red", "amber"], "green")

m.to_csv("master_dashboard_data.csv")

print(m.voltage_status.value_counts(normalize=True).round(3) * 100)
print("Mean voltage compliance (%):", round(m.voltage_compliance_pct.mean(), 1))
print("Worst voltage compliance (%):", round(m.voltage_compliance_pct.min(), 1))
print("Time with reverse flow (%):", round(100 * (m.grid_mw < 0).mean(), 1))
print("Peak PV penetration (%):", round(m.pv_penetration_pct.max(), 1))
print("Battery energy charged (MWh):", round(m.batt_mw[m.batt_mw > 0].sum() * 0.5, 2))
print("Battery energy discharged (MWh):", round(-m.batt_mw[m.batt_mw < 0].sum() * 0.5, 2))
print("Peak customers out:", m.customers_out.max())
print("Mean comms success (%):", round(m.comm_success_pct.mean(), 1))