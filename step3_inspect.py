import pandapower as pp
import pandapower.networks as pn
import matplotlib.pyplot as plt

net = pn.case33bw()
pp.runpp(net)

print(net.load[["bus", "p_mw", "q_mvar"]].head())
print("Total load (MW):", net.load.p_mw.sum())

plt.plot(net.res_bus.vm_pu.values, marker="o")
plt.axhline(0.95, color="red", linestyle="--")
plt.xlabel("Bus number")
plt.ylabel("Voltage (pu)")
plt.show()

below = (net.res_bus.vm_pu < 0.95).sum()
print("Buses below 0.95 pu:", below)
print("Voltage compliance (%):", 100 * (33 - below) / 33)