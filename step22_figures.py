import pandas as pd
import matplotlib.pyplot as plt

m = pd.read_csv("master_dashboard_data.csv", index_col=0)
m.index = pd.to_datetime(m.index, utc=True).tz_convert("Europe/London")
m["hour"] = m.index.hour + m.index.minute / 60

def day(d):
    return m[m.index.strftime("%Y-%m-%d") == d]

d5, d7, d4 = day("2026-08-05"), day("2026-08-07"), day("2026-08-04")

plt.rcParams.update({"font.size": 7, "axes.titlesize": 7, "axes.labelsize": 7,
                     "legend.fontsize": 6, "xtick.labelsize": 6, "ytick.labelsize": 6})
fig, ax = plt.subplots(2, 3, figsize=(7.16, 4.0))

# (a) outage, 5 Aug
ax[0, 0].plot(d5.hour, d5.load_mw, label="Load")
ax[0, 0].plot(d5.hour, d5.pv_mw, label="PV")
ax[0, 0].plot(d5.hour, d5.grid_mw, label="Grid import")
ax[0, 0].set_title("(a) 5 Aug: outage")
ax[0, 0].set_ylabel("MW")
ax[0, 0].set_ylim(-1.4, 3.6)
ax[0, 0].legend(loc="upper center", ncol=3, frameon=False)
ax[1, 0].plot(d5.hour, d5.customers_out, color="C3")
ax[1, 0].set_ylabel("Customers out")

# (b) overvoltage and reverse flow, 7 Aug
ax[0, 1].plot(d7.hour, d7.max_v, label="Highest")
ax[0, 1].plot(d7.hour, d7.min_v, label="Lowest")
ax[0, 1].axhline(1.05, color="r", ls="--", lw=0.8)
ax[0, 1].axhline(0.95, color="r", ls="--", lw=0.8)
ax[0, 1].set_title("(b) 7 Aug: overvoltage")
ax[0, 1].set_ylabel("Voltage (pu)")
ax[0, 1].set_ylim(0.94, 1.085)
ax[0, 1].legend(loc="upper center", ncol=2, frameon=False)
ax[1, 1].plot(d7.hour, d7.grid_mw, color="C2")
ax[1, 1].axhline(0, color="k", lw=0.6)
ax[1, 1].set_ylabel("Grid import (MW)")

# (c) evening under-voltage, 4 Aug
ax[0, 2].plot(d4.hour, d4.max_v, label="Highest")
ax[0, 2].plot(d4.hour, d4.min_v, label="Lowest")
ax[0, 2].axhline(1.05, color="r", ls="--", lw=0.8)
ax[0, 2].axhline(0.95, color="r", ls="--", lw=0.8)
ax[0, 2].set_title("(c) 4 Aug: under-voltage")
ax[0, 2].set_ylabel("Voltage (pu)")
ax[0, 2].set_ylim(0.94, 1.085)
ax[0, 2].legend(loc="upper center", ncol=2, frameon=False)
ax[1, 2].plot(d4.hour, d4.soc_mwh, color="C4")
ax[1, 2].set_ylabel("Battery energy (MWh)")

for a in ax[1]:
    a.set_xlabel("Hour of day")
for a in ax.flat:
    a.set_xticks([0, 6, 12, 18, 24])
    a.set_xlim(0, 24)
    a.grid(alpha=0.3)

fig.tight_layout()
fig.savefig("fig_scenarios.png", dpi=300)

# ---------- values to quote in Section VII (also saved to fig_values.txt) ----------
lines = []
def say(text):
    print(text)
    lines.append(text)

out = d5[d5.customers_out > 0]
say(f"5 Aug outage first slot: {out.index[0].strftime('%H:%M')} | last slot: "
    f"{out.index[-1].strftime('%H:%M')} | customers: {out.customers_out.max()}")

say(f"7 Aug highest voltage: {round(d7.max_v.max(), 3)} at {d7.max_v.idxmax().strftime('%H:%M')}")
say(f"7 Aug lowest grid import (MW): {round(d7.grid_mw.min(), 2)} at {d7.grid_mw.idxmin().strftime('%H:%M')}")
say(f"7 Aug reverse flow (%): {round(100 * (d7.grid_mw < 0).mean(), 1)}")
say(f"7 Aug battery energy range (MWh): {round(d7.soc_mwh.min(), 2)} to {round(d7.soc_mwh.max(), 2)}")

say(f"4 Aug lowest voltage: {round(d4.min_v.min(), 3)} at {d4.min_v.idxmin().strftime('%H:%M')}")
say(f"4 Aug battery peak energy (MWh): {round(d4.soc_mwh.max(), 2)}")
dis = d4[d4.batt_mw < 0]
if len(dis) > 0:
    say(f"4 Aug discharge first slot: {dis.index[0].strftime('%H:%M')} | last slot: "
        f"{dis.index[-1].strftime('%H:%M')}")
    floor = d4[(d4.soc_mwh <= 0.2001) & (d4.index > dis.index[0])]
    if len(floor) > 0:
        say(f"4 Aug battery first at floor: {floor.index[0].strftime('%H:%M')}")

say(f"Whole window reverse flow (%): {round(100 * (m.grid_mw < 0).mean(), 1)}")

with open("fig_values.txt", "w") as f:
    f.write("\n".join(lines))

plt.show()