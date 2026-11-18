import numpy as np
import pandas as pd

m = pd.read_csv("master_dashboard_data.csv", index_col=0)
b = pd.read_csv("results_bess_2mwh.csv", index_col=0)
log = pd.read_csv("outage_log.csv")

RATED_MW, BESS_MWH, CUSTOMERS = 3.715, 2.0, 2476

def low_good(x, g, a):
    return "green" if x < g else "amber" if x <= a else "red"

def high_good(x, g, a):
    return "green" if x >= g else "amber" if x >= a else "red"

rows = []

util = 100 * m.grid_mw.max() / RATED_MW
rows.append(("Feeder utilization (peak)", util, "%", low_good(util, 80, 100)))

par = m.load_mw.max() / m.load_mw.mean()
rows.append(("Peak-to-average ratio", par, "ratio", low_good(par, 1.5, 2.0)))

pvp = m.pv_penetration_pct.max()
rows.append(("PV penetration (peak)", pvp, "%", low_good(pvp, 50, 80)))

rows.append(("PV curtailment", 0.0, "%", "not modelled"))

soc = 100 * m.soc_mwh / BESS_MWH
red = (soc < 9.99) | (soc > 90.01)
green = (soc >= 20) & (soc <= 80)
amber = ~red & ~green
rows.append(("BESS SOC in green band (20-80%)", 100 * green.mean(), "% of time", "info"))
rows.append(("BESS SOC in amber band", 100 * amber.mean(), "% of time", "info"))
rows.append(("BESS SOC in red band", 100 * red.mean(), "% of time", "info"))

charged = b.batt_mw[b.batt_mw > 0].sum() * 0.5
discharged = -b.batt_mw[b.batt_mw < 0].sum() * 0.5
rte = 100 * discharged / charged
rows.append(("BESS round-trip efficiency", rte, "%", high_good(rte, 90, 80)))

saidi = log.customer_minutes.sum() / CUSTOMERS
saifi = log.customers.sum() / CUSTOMERS
rows.append(("SAIDI (14 days)", saidi, "min/customer", "needs utility target"))
rows.append(("SAIFI (14 days)", saifi, "interruptions/customer", "needs utility target"))

bad = b.n_low + b.n_high
vc = 100 * (1 - bad.sum() / (33 * len(b)))
rows.append(("Voltage compliance (bus-time samples)", vc, "%", high_good(vc, 99, 95)))

rows.append(("Voltage unbalance", np.nan, "%", "not available (balanced model)"))

cm = m.comm_success_pct.mean()
rows.append(("Meter communication success", cm, "%", high_good(cm, 99, 95)))

pq = 100 * (bad > 0).mean()
rows.append(("Voltage alarm rate", pq, "% of intervals", low_good(pq, 1, 5)))

kpi = pd.DataFrame(rows, columns=["KPI", "Value", "Unit", "Status"])
kpi["Value"] = kpi["Value"].round(2)
print(kpi.to_string(index=False))
kpi.to_csv("kpi_table_results.csv", index=False)