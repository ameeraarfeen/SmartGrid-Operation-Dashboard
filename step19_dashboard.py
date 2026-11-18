import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Smart Grid Operation Dashboard", layout="wide")

@st.cache_data
def load_data():
    d = pd.read_csv("master_dashboard_data.csv", index_col=0)
    d.index = pd.to_datetime(d.index, utc=True).tz_convert("Europe/London")
    return d

m = load_data()

st.title("Integrated Smart Grid Operation Dashboard")
st.caption("IEEE 33-bus feeder | UKPN smart meter load, modelled PV, voltage-aware BESS | 3-16 Aug 2026")

# ---- Sidebar: date range and status legend ----
days = sorted(set(m.index.date))
d1, d2 = st.sidebar.select_slider("Date range", options=days, value=(days[0], days[-1]))

st.sidebar.markdown("### Status colours")
st.sidebar.markdown(
    "**Voltage**  \n"
    "🟢 all buses 0.95 to 1.05 pu  \n"
    "🟠 any bus outside 0.95 to 1.05 pu  \n"
    "🔴 any bus below 0.94 or above 1.06 pu  \n\n"
    "**Meter comms**  \n"
    "🟢 98% or more reporting  \n"
    "🟠 95% to 98%  \n"
    "🔴 below 95%"
)

day_col = pd.Series(m.index.date, index=m.index)
view = m[day_col.between(d1, d2)]

# ---- Status tiles (two rows of three) ----
icons = {"green": "🟢", "amber": "🟠", "red": "🔴"}
order = ["green", "amber", "red"]
worst_v = max(view.voltage_status.unique(), key=order.index)
worst_c = max(view.comm_status.unique(), key=order.index)

row1 = st.columns(3)
row1[0].metric("Voltage status (worst)", f"{icons[worst_v]} {worst_v}")
row1[1].metric("Voltage compliance (mean)", f"{view.voltage_compliance_pct.mean():.1f}%")
row1[2].metric("Reverse flow (share of time)", f"{100 * (view.grid_mw < 0).mean():.1f}%")

row2 = st.columns(3)
row2[0].metric("PV penetration (peak)", f"{view.pv_penetration_pct.max():.0f}%")
row2[1].metric("Customers out (peak)", f"{view.customers_out.max():.0f}")
row2[2].metric("Meter comms (mean)", f"{icons[worst_c]} {view.comm_success_pct.mean():.1f}%")

# ---- Chart helper ----
def chart(cols, title, ylabel, hlines=(), yrange=None):
    fig = go.Figure()
    for col, name in cols:
        fig.add_trace(go.Scatter(x=view.index, y=view[col], name=name))
    for y in hlines:
        fig.add_hline(y=y, line_dash="dash", line_color="red")
    if yrange:
        fig.update_yaxes(range=yrange)
    fig.update_layout(title=title, yaxis_title=ylabel, height=300,
                      margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig)

# ---- Charts ----
left, right = st.columns(2)
with left:
    chart([("load_mw", "Feeder load"), ("pv_mw", "PV"), ("grid_mw", "Grid import")],
          "Demand, PV and grid import", "MW")
    chart([("batt_mw", "Battery power (+charge)")], "Battery power", "MW")
    chart([("customers_out", "Customers out")], "Outages", "Customers",
      yrange=[0, max(1, view.customers_out.max() * 1.1)])
with right:
    chart([("min_v", "Lowest voltage"), ("max_v", "Highest voltage")],
          "Voltage envelope", "pu", hlines=[0.95, 1.05])
    chart([("soc_mwh", "Stored energy")], "Battery state of charge", "MWh")
    chart([("comm_success_pct", "Comms success")],
          "Smart meter communication", "%", yrange=[90, 100])

# ---- Alarm log ----
st.subheader("Alarm log")
alarms = view[(view.voltage_status != "green") | (view.comm_status != "green")]
st.dataframe(alarms[["min_v", "max_v", "voltage_compliance_pct",
                     "voltage_status", "comm_status"]].round(3))