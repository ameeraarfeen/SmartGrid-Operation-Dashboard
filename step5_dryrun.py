import numpy as np
import pandas as pd
import pandapower as pp
import pandapower.networks as pn
import matplotlib.pyplot as plt

times = pd.date_range("2024-01-01", periods=1344, freq="15min")
hours = np.array(times.hour + times.minute / 60)
profile = 0.65 + 0.35 * np.sin((hours - 13) * 2 * np.pi / 24)

net = pn.case33bw()
base_p = net.load.p_mw.copy()
base_q = net.load.q_mvar.copy()

min_v = []
below_count = []
for k in range(len(times)):
    net.load.p_mw = base_p * profile[k]
    net.load.q_mvar = base_q * profile[k]
    pp.runpp(net, numba=False)
    min_v.append(net.res_bus.vm_pu.min())
    below_count.append((net.res_bus.vm_pu < 0.95).sum())

compliance = 100 * (33 - pd.Series(below_count, index=times)) / 33
print("Worst compliance (%):", compliance.min())
print("Best compliance (%):", compliance.max())
compliance.plot()
plt.ylabel("Voltage compliance (%)")
plt.show()