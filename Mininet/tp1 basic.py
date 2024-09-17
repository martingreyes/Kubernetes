#!/usr/bin/python

from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch
from mininet.node import Node

def myNetwork():

    net = Mininet( topo=None, build=False, ipBase='192.168.100.0/24')

    info('\n*** Add switches')
    s1, s2 , ss1 , ss2 = [
        net.addSwitch(s, cls=OVSKernelSwitch, failMode='standalone')
        for s in ('s1', 's2', 'ss1' , 'ss2')
    ]

    info('\n*** Add routers')
    rc = net.addHost('rc', ip="192.168.100.6")
    r1 = net.addHost('r1',ip="192.168.100.1")
    r2 = net.addHost('r2', ip="192.168.100.9")

    rc.cmd('sysctl net.ipv4.ip_forward=1')
    r1.cmd('sysctl net.ipv4.ip_forward=1')
    r2.cmd('sysctl net.ipv4.ip_forward=1')

    info('\n*** Add hosts')
    h1 = net.addHost('h1', ip='10.0.1.254/24')
    h2 = net.addHost('h2', ip='10.0.2.254/24')

    info('\n*** Add links')
    net.addLink(rc, s1, intfName1='rcs1-eth0', params1={'ip': '192.168.100.6/29'})
    net.addLink(rc, s2, intfName1='rcs2-eth0', params1={'ip': '192.168.100.14/29'})

    net.addLink(r1, s1, intfName1='r1s1-eth0', params1={'ip': '192.168.100.1/29'})
    net.addLink(r2, s2, intfName1='r2s2-eth0', params1={'ip': '192.168.100.9/29'})

    net.addLink(r1, ss1, intfName1='r1ss1-eth0', params1={'ip': '10.0.1.1/24'})
    net.addLink(r2, ss2, intfName1='r2ss2-eth0', params1={'ip': '10.0.2.1/24'})

    net.addLink(h1, ss1, intfName1='h1ss1-eth0', params1={'ip': '10.0.1.254/24'})
    net.addLink(h2, ss2, intfName1='h2ss2-eth0', params1={'ip': '10.0.2.254/24'})

    info('\n*** Starting network ')
    net.build()

    info('\n*** Creating routes:')
    
    info('\n- from h1 to r1',h1.cmd('ip r add 192.168.100.0/29 via 10.0.1.1 dev h1ss1-eth0')) # ya que 192.168.100.0/29 contiene 192.168.100.1/29 y 192.168.100.6/29
    info('\n- from h1 to r2',h1.cmd('ip r add 192.168.100.8/29 via 10.0.1.1 dev h1ss1-eth0')) # ya que 192.168.100.8/29 contiene 192.168.100.9/29 y 192.168.100.14/29
    info('\n- from h1 to h2',h1.cmd('ip r add 10.0.2.0/24 via 10.0.1.1 dev h1ss1-eth0'))

    info('\n- from h2 to r2',h2.cmd('ip r add 192.168.100.8/29 via 10.0.2.1 dev h2ss2-eth0')) # ya que 192.168.100.8/29 contiene 192.168.100.9/29 y 192.168.100.14/29
    info('\n- from h2 to r1',h2.cmd('ip r add 192.168.100.0/29 via 10.0.2.1 dev h2ss2-eth0')) # ya que 192.168.100.0/29 contiene 192.168.100.1/29 y 192.168.100.6/29
    info('\n- from h2 to h1',h2.cmd('ip r add 10.0.1.0/24 via 10.0.2.1 dev h2ss2-eth0'))

    info('\n- from r1 to r2',r1.cmd('ip r add 192.168.100.8/29 via 192.168.100.6 dev r1s1-eth0'))
    info('\n- from r1 to h2',r1.cmd('ip r add 10.0.2.0/24 via 192.168.100.6 dev r1s1-eth0'))
    #? No hace falta rutearlo a rc ya que como r1 y rc son vecinos lo hace automatico (?)

    info('\n- from r2 to r1',r2.cmd('ip r add 192.168.100.0/29 via 192.168.100.14 dev r2s2-eth0'))
    info('\n- from r2 to h1',r2.cmd('ip r add 10.0.1.0/24 via 192.168.100.14 dev r2s2-eth0'))
    #? No hace falta rutearlo a rc ya que como r2 y rc son vecinos lo hace automatico (?)

    info('\n- from rc to h1',rc.cmd('ip r add 10.0.1.0/24 via 192.168.100.1 dev rcs1-eth0'))
    info('\n- from rc to h2',rc.cmd('ip r add 10.0.2.0/24 via 192.168.100.9 dev rcs2-eth0'))
    #? No hace falta rutearlo a r1 ya que como rc y r1 son vecinos lo hace automatico (?)
    #? No hace falta rutearlo a r2 ya que como rc y r2 son vecinos lo hace automatico (?)


    # info('\n\n*** Starting controllers')
    for controller in net.controllers:
        controller.start()

    # info('\n*** Starting switches ')
    for s in (s1, s2 , ss1 , ss2):
        s.start([])

    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

# mininet> pingall
# *** Ping: testing ping reachability
# rc -> r1 r2 h1 h2 
# r1 -> rc r2 h1 h2 
# r2 -> rc r1 h1 h2 
# h1 -> rc r1 r2 h2 
# h2 -> rc r1 r2 h1 
# *** Results: 0% dropped (20/20 received)

# mininet> h1 route
# Kernel IP routing table
# Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
# 10.0.1.0        0.0.0.0         255.255.255.0   U     0      0        0 h1ss1-eth0
# 10.0.2.0        10.0.1.1        255.255.255.0   UG    0      0        0 h1ss1-eth0
# 192.168.100.0   10.0.1.1        255.255.255.248 UG    0      0        0 h1ss1-eth0
# 192.168.100.8   10.0.1.1        255.255.255.248 UG    0      0        0 h1ss1-eth0

# mininet> r1 route
# Kernel IP routing table
# Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
# 10.0.1.0        0.0.0.0         255.255.255.0   U     0      0        0 r1ss1-eth0
# 10.0.2.0        192.168.100.6   255.255.255.0   UG    0      0        0 r1s1-eth0
# 192.0.0.0       0.0.0.0         255.0.0.0       U     0      0        0 r1s1-eth0
# 192.168.100.8   192.168.100.6   255.255.255.248 UG    0      0        0 r1s1-eth0

# mininet> rc route
# Kernel IP routing table
# Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
# 10.0.1.0        192.168.100.1   255.255.255.0   UG    0      0        0 rcs1-eth0
# 10.0.2.0        192.168.100.9   255.255.255.0   UG    0      0        0 rcs2-eth0
# 192.0.0.0       0.0.0.0         255.0.0.0       U     0      0        0 rcs1-eth0
# 192.168.100.8   0.0.0.0         255.255.255.248 U     0      0        0 rcs2-eth0

# mininet> r2 route
# Kernel IP routing table
# Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
# 10.0.1.0        192.168.100.14  255.255.255.0   UG    0      0        0 r2s2-eth0
# 10.0.2.0        0.0.0.0         255.255.255.0   U     0      0        0 r2ss2-eth0
# 192.0.0.0       0.0.0.0         255.0.0.0       U     0      0        0 r2s2-eth0
# 192.168.100.0   192.168.100.14  255.255.255.248 UG    0      0        0 r2s2-eth0

# mininet> h2 route
# Kernel IP routing table
# Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
# 10.0.1.0        10.0.2.1        255.255.255.0   UG    0      0        0 h2ss2-eth0
# 10.0.2.0        0.0.0.0         255.255.255.0   U     0      0        0 h2ss2-eth0
# 192.168.100.0   10.0.2.1        255.255.255.248 UG    0      0        0 h2ss2-eth0
# 192.168.100.8   10.0.2.1        255.255.255.248 UG    0      0        0 h2ss2-eth0