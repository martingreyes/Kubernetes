#!/usr/bin/python

from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch
from mininet.node import Node


def add_switches(net,cantidad):
    info('\n*** Add switches')
    nombres = []
    for x in range(sucursales):
        nombres.append("s{}".format(x + 1))
        nombres.append("ss{}".format(x + 1))
    switches = [net.addSwitch(s, cls=OVSKernelSwitch, failMode='standalone') for s in nombres]
    return switches


def add_routers(net,cantidad):
    info('\n*** Add routers')
    routers = []
    routers.append("rc")
    for x in range (cantidad):
        routers.append("r{}".format(x + 1))
            
    ip = 1
    result = []
    for router in routers:
        if router == routers[0]:
            router = net.addHost('rc', ip="192.168.100.6")
            router.cmd('sysctl net.ipv4.ip_forward=1')
        else:
            router = net.addHost(router, ip="192.168.100.{}".format(ip))
            router.cmd('sysctl net.ipv4.ip_forward=1')
            ip = ip + 8
        
        result.append(router)
    
    return result

def add_hosts(net,cantidad):
    info('\n*** Add hosts')
    hosts = []
    for x in range(cantidad):
        hosts.append("h{}".format(x + 1))

    ip = 1

    result = []

    for host in hosts:
        host = net.addHost(host, ip="10.0.{}.254/24".format(ip))
        result.append(host)
        ip = ip + 1

    return result


def add_links(net,cantidad,switches,routers,hosts):
    info('\n*** Add links')
    #Links de rc a los sx
    ip = 6
    indice_switches = 0
    for x in range(int(len(switches)/2)):
        net.addLink(routers[0], switches[indice_switches], intfName1="rcs{}-eth0".format(x+1), params1={'ip': '192.168.100.{}/29'.format(ip)})
        ip = ip + 8
        indice_switches + 2

    #Links de los rx a los sx
    ip = 1
    indice_switches = 0
    for x in range(int(len(switches)/2)):
        net.addLink(routers[x + 1], switches[indice_switches], intfName1="r{}s{}-eth0".format(x+1,x+1), params1={'ip': '192.168.100.{}/29'.format(ip)})
        ip = ip + 8
        indice_switches + 2

    #Links de los rx a los ssx
    ip = 1
    indice_switches = 1
    for x in range(int(len(switches)/2)):
        net.addLink(routers[x + 1], switches[indice_switches], intfName1="r{}ss{}-eth0".format(x+1,x+1), params1={'ip': '10.0.{}.1/24'.format(ip)})
        ip = ip + 1
        indice_switches + 2

    #Links de los hx a los ssx
    ip = 1
    indice_switches = 1
    for x in range(int(len(switches)/2)):
        net.addLink(hosts[x], switches[indice_switches], intfName1="h{}ss{}-eth0".format(x+1,x+1), params1={'ip': '10.0.{}.254/24'.format(ip)})
        ip = ip + 1
        indice_switches + 2





def create_routes(net,sucursales,switches,routers,hosts):
    info('\n*** Creating routes:')

    rc = routers[0]

   #Host routes 
    sin_rc = routers
    sin_rc.pop(0)
    cont = 1
    i = 1
    for host in hosts:
        ip = 0
        for router in sin_rc:
            #from hx to rx 
            info('\n- from {} to {}'.format(host,router),host.cmd('ip r add 192.168.100.{}/29 via 10.0.{}.1 dev h{}ss{}-eth0'.format(ip,i,cont,cont)))
            ip = ip + 8 
        
        #from hx to hy
        sin_host = []
        for x in range(sucursales):
            if "h{}".format(x+1) != "h{}".format(i):
                sin_host.append("h{}".format(x+1))

        for x in sin_host:
            caracteres = []
            for caracter in x:
                caracteres.append(caracter)
            info('\n- from {} to {}'.format(host,x),host.cmd('ip r add 10.0.{}.0/24 via 10.0.{}.1 dev h{}ss{}-eth0'.format(caracteres[1],i,cont,cont)))

        cont = cont +1 
        i = i + 1


    #Routers routes
    contador = 1
    ip = 6
    for router in routers:

        sin_router = []
        for x in range(sucursales):
           if "r{}".format(x+1) != "r{}".format(contador):
                sin_router.append("r{}".format(x+1))

        for x in sin_router:
            caracteres = []
            for caracter in x:
                caracteres.append(caracter)

            otra_ip = 0
            for x in range(int(caracteres[1]) - 1):
                otra_ip = otra_ip + 8

            info('\n- from {} to r{}'.format(router,caracteres[1]),router.cmd('ip r add 192.168.100.{}/29 via 192.168.100.{} dev r{}s{}-eth0'.format(otra_ip,ip,contador,contador)))
            info('\n- from {} to h{}'.format(router,caracteres[1]),router.cmd('ip r add 10.0.{}.0/24 via 192.168.100.{} dev r{}s{}-eth0'.format(caracteres[1],ip,contador,contador)))

        contador = contador + 1
        ip = ip + 8

        
    #Router Central routes
    #TODO
    contador = 1
    ip = 1
    for host in hosts:
        info('\n- from rc to {}'.format(host),rc.cmd('ip r add 10.0.{}.0/24 via 192.168.100.{} dev rcs{}-eth0'.format(contador, ip, contador)))
        ip = ip + 8
        contador = contador + 1



    
def myNetwork(sucursales):
    net = Mininet( topo=None, build=False, ipBase='192.168.100.0/24')

    switches = add_switches(net,sucursales)

    routers = add_routers(net,sucursales)

    hosts = add_hosts(net,sucursales)

    add_links(net,sucursales,switches,routers,hosts)

    info('\n*** Starting network ')
    net.build()

    create_routes(net,sucursales,switches,routers,hosts)

    # info('\n\n*** Starting controllers')
    for controller in net.controllers:
        controller.start()

        # info('\n*** Starting switches ')
    for switch in switches:
        switch.start([])

    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    sucursales = str(input("\nCantidad de sucursales (max 6): "))
    while not sucursales.isdigit() or int(sucursales) > 6 or int(sucursales) < 1:
        sucursales = input("\nCantidad de sucursales (max 6): ")
    sucursales = int(sucursales)
    myNetwork(sucursales)
