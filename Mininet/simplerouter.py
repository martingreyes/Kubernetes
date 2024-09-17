#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch


def myNetwork():
    net = Mininet(topo=None, build=False, ipBase='192.168.0.0/16')

    info('*** Add switches\n')
    s1, s2, s3 = [
        net.addSwitch(s, cls=OVSKernelSwitch, failMode='standalone')
        for s in ('s1', 's2', 's3')
    ]

    info('*** Add router\n')
    router = net.addHost('r0', ip='192.168.1.1/24')
    router.cmd('sysctl net.ipv4.ip_forward=1')

    info('*** Add hosts\n')
    h1 = net.addHost('h1', ip='192.168.1.100/24') #, defaultRoute='via 192.168.1.1')
    h2 = net.addHost('h2', ip='192.168.2.100/24') #, defaultRoute='via 192.168.2.1')
    h3 = net.addHost('h3', ip='192.168.3.100/24') #, defaultRoute='via 192.168.3.1')

    info('*** Add router links\n')
    net.addLink(s1, router, intfName2='r0-eth1', params2={'ip': '192.168.1.1/24'})
    net.addLink(s2, router, intfName2='r0-eth2', params2={'ip': '192.168.2.1/24'})
    net.addLink(s3, router, intfName2='r0-eth3', params2={'ip': '192.168.3.1/24'})

    info('*** Add hosts links\n')
    for h, s in [(h1, s1), (h2, s2), (h3, s3)]:
        net.addLink(h, s)

    info('*** Starting network\n')
    net.build()

    info(h1.cmd('ip r add 192.168.0.0/22 via 192.168.1.1'))
    info(h2.cmd('ip r add 192.168.0.0/22 via 192.168.2.1'))
    info(h3.cmd('ip r add 192.168.0.0/22 via 192.168.3.1'))

    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches\n')
    for s in (s1, s2, s3):
        s.start([])
    info('*** Post configure switches and hosts\n')

    net.start()

    info(router.cmd('ip r'))
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
