from mininet.net import Mininet
from mininet.node import RemoteController

net = Mininet(controller=None)

# Add controller and switches to the network
c0 = net.addController(name='c0', controller=RemoteController, ip='localhost', protocol='tcp', port=6653)
c1 = net.addController(name='c1', controller=RemoteController, ip='localhost', protocol='tcp', port=6654)
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
s3 = net.addSwitch('s3')

# Connect switches to each other
net.addLink(s1,s2)
net.addLink(s1,s3)

# Add hosts and connect them to s1
h1 = net.addHost('h1', ip='10.1.0.1/24')
net.addLink(h1, s1)
h2 = net.addHost('h2', ip='10.2.0.2/24')
net.addLink(h2, s1)
h3 = net.addHost('h3', ip='10.3.0.3/24')
net.addLink(h3, s1)

# Add hosts and connect them to s2
h4 = net.addHost('h4', ip='10.1.0.4/24')
net.addLink(h4, s2)
h5 = net.addHost('h5', ip='10.2.0.5/24')
net.addLink(h5, s2)
h6 = net.addHost('h6', ip='10.3.0.6/24')
net.addLink(h6, s2)

# Add hosts and connect them to s3
h7 = net.addHost('h7', ip='10.1.0.7/24')
net.addLink(h7, s3)
h8 = net.addHost('h8', ip='10.2.0.8/24')
net.addLink(h8, s3)
h9 = net.addHost('h9', ip='10.3.0.9/24')
net.addLink(h9, s3)

net.start()
h1.setDefaultRoute('via 10.1.0.254')
h2.setDefaultRoute('via 10.2.0.254')
h3.setDefaultRoute('via 10.3.0.254')
h4.setDefaultRoute('via 10.1.0.254')
h5.setDefaultRoute('via 10.2.0.254')
h6.setDefaultRoute('via 10.3.0.254')
h7.setDefaultRoute('via 10.1.0.254')
h8.setDefaultRoute('via 10.2.0.254')
h9.setDefaultRoute('via 10.3.0.254')
net.interact()
