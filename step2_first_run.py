import pandapower as pp
import pandapower.networks as pn

net = pn.case33bw()
pp.runpp(net)

print(net.bus.shape)
print(net.res_bus.vm_pu.min())