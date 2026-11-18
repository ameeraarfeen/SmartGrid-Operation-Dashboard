import numpy as np
import pandas as pd
import pandapower.networks as pn
import pandapower.topology as top

times = pd.date_range("2026-08-03", periods=672, freq="30min", tz="Europe/London")
net = pn.case33bw()

cust = np.zeros(33)
cust[net.load.bus.values] = np.round(net.load.p_mw.values * 1000 / 1.5)
total = cust.sum()

events = [("2026-08-05 14:00", 4, 5),
          ("2026-08-10 19:00", 3, 12),
          ("2026-08-13 03:00", 2, 25)]

log = []
out_series = pd.Series(0.0, index=times)
for start, n_slots, line in events:
    net.line.at[line, "in_service"] = False
    dead = sorted(top.unsupplied_buses(net))
    net.line.at[line, "in_service"] = True
    ci = cust[dead].sum()
    dur = n_slots * 30
    t0 = pd.Timestamp(start, tz="Europe/London")
    t1 = t0 + pd.Timedelta(minutes=30 * (n_slots - 1))
    out_series.loc[t0:t1] = ci
    log.append(dict(start=t0, line=line, duration_min=dur, buses_lost=len(dead),
                    customers=ci, customer_minutes=ci * dur))

log_df = pd.DataFrame(log)
saifi = log_df.customers.sum() / total
saidi = log_df.customer_minutes.sum() / total
print(log_df.to_string())
print("Total customers:", total)
print("SAIFI (per customer):", round(saifi, 3))
print("SAIDI (min per customer):", round(saidi, 1))
print("CAIDI (min per interruption):", round(saidi / saifi, 1))

log_df.to_csv("outage_log.csv", index=False)
out_series.to_csv("customers_out.csv")