# Open-vSwitch for dummies
This is meant to be a 1:1 copy of the Open vSwitch tutorial that only highlights the hands-on information.

## Topics
- OVS Faucet Tutorial
- OVS IPsec Tutorial
- Open vSwitch Advanced Features
- OVS Conntrack Tutorial

## Approach

For this Tutorial we followed the guide from [Open-vSwitch](https://docs.openvswitch.org/en/latest/tutorials/) while trying to make it simple enough to recall the most important stuff.

## Requirements

- Docker

# Guide
## OVS Faucet Tutorial
#### Setting up OVS
```bash
git clone https://github.com/openvswitch/ovs.git
cd ovs
```

You will need to setup a sandbox, to do so you will need to use the following commands:

```bash
sudo apt-get build-dep openvswitch
./boot.sh
./configure
make -j4
```

To run the sandbox you will need to use:
```bash
make sandbox
```
You can confirm you're inside the sandbox by running a simple **ls** command.
If you want to exit the sandbox you can easily do it with either **exit** or Ctrl+D

#### Setting up Faucet
```bash
git clone https://github.com/faucetsdn/faucet.git
cd faucet
```
Checkout the latest tag
```bash
latest_tag=$(git describe --tags $(git rev-list --tags --max-count=1))
git checkout $latest_tag
```
To use faucet you will have to build a docker container image. You can do it with the following command, *should take a few minutes*.
```bash
sudo docker build -t faucet/faucet -f Dockerfile.faucet .
```
Create a installation directory under the **faucet** directory for the docker image to use
```bash
mkdir inst
```
>The faucet configuration will go in **inst/faucet.yaml** and its main log will appear in **inst/faucet.log**.

Now you will need to create a container and start Faucet.
```bash
sudo docker run -d --name faucet --restart=always -v $(pwd)/inst/:/etc/faucet/ -v $(pwd)/inst/:/var/log/faucet/ -p 6653:6653 -p 9302:9302 faucet/faucet
```

> Later on, to make a new or updated Faucet configuration take effect quickly you can run:
    ```
    sudo docker exec faucet pkill -HUP -f faucet.faucet
    ```

#### Overview
The tutorial covers the following topics:
1. **Switching**: Set up an L2 network with Faucet.
2. **Routing**: Route between multiple L3 networks with Faucet.
3. **ACLs**: Add and modify access control rules.

Structure:
1. **Faucet**:
    1. Top level in the system, this is the authoritative source of the network configuration.
    2. Connects to a variety of monitoring performance tools.
    3. We use **faucet.yaml** for configuration and **faucet.log** to observe state and **to check erros within our set up process**.
2. **OpenFlow**:
    1. Standardized by the Open Networking Foundation, that controllers like Faucet use to control how Open vSwitch and other switches treat packets in the network.
    2. We use **ovs-ofctl** to observe and modify Open vSwitch's OpenFlow behavior as well as **ovs-appctl** for communicating with **ovs-vswitch** and other Open vSwitch daemons, to ask "what-if?" type questions.
    3. The OVS sandbox raises the Open vSwitch logging level for OpenFlow high enough for us to understand its behavior by reading the log file.
3. **Open vSwitch datapath**
    1. Cache designed to accelerate packet processing

#### Switching
As stated in the Overview Section, will set up a L2 network, for that we need to put the following into **inst/faucet.yaml**
```yaml
dps:
    switch-1:
        dp_id: 0x1
        timeout: 11800
        arp_neighbor_timeout: 3600
        interfaces:
            1:
                native_vlan: 100
            2:
                native_vlan: 100
            3:
                native_vlan: 100
            4:
                native_vlan: 200
            5:
                native_vlan: 200
vlans:
    100:
    200:
```
**Brief**: 
Defines a single switch ("datapath" or "dp") named **switch-1**, with 5 ports; Ports 1, 2 and 3 are in VLAN 100, while ports 4 and 5 are in VLAN 2. Faucet can identify the switch from its datapath ID, defined by the **dp_id** field.

> On the official website the **timeout** and **arp_neighbor_timeout** fields are both set to 3600, however, following the tutorial we found out that the former should be greater than twice the value of the later.

Now you need to restart Faucet, in order to apply this configuration.
```bash
sudo docker restart faucet
```
If the configuration update is successful, you should see a new line of type **INFO** at the end of **inst/faucet.log** with the added DPIP
```bash
cat faucet.log | grep "faucet INFO"
```

If that proved to be the case, Faucet is waiting for a switch with DPID 0x1 to connect to it over OpenFlow, so the next step is to create a switch with OVS and make it connect to Faucet.
> Switch to the terminal where you checked out ovs and start the sandbox

Inside the sandbox, create a switch "bridge" named **br0** with the DPID 0x1 and add simulated ports to it. For the sake of simplicity we connect port1 to p1, port2 to p2, and so on. One last detail is setting the controller to be "out-of-band" to avoid annoying messages in the **ovs-vswitchd** logs.

> More information can be found by running ```man ovs-vswitchd.conf.db``` and searching for **connection_node**

```bash
ovs-vsctl add-br br0 \
         -- set bridge br0 other-config:datapath-id=0000000000000001 \
         -- add-port br0 p1 -- set interface p1 ofport_request=1 \
         -- add-port br0 p2 -- set interface p2 ofport_request=2 \
         -- add-port br0 p3 -- set interface p3 ofport_request=3 \
         -- add-port br0 p4 -- set interface p4 ofport_request=4 \
         -- add-port br0 p5 -- set interface p5 ofport_request=5 \
         -- set-controller br0 tcp:127.0.0.1:6653 \
         -- set controller br0 connection-mode=out-of-band
```
Due to Faucet requirements we need to set the ports state to be up, to do so, we run the command:
```bash
ovs-appctl netdev-dummy/set-admin-state up
```

Now, if you look at **inst/faucet.log** again, you should see that Faucet recognized and configured the new switch and its ports.

```bash
cat faucet.log | grep "faucet.valve INFO"
```

To see the related activity on the OVS side you need to look in **sandbox/ovs-vswitch.log**

```bash

vconn|DBG|tcp:127.0.0.1:6653: sent (Success): OFPST_PORT_DESC reply (OF1.3) (xid=0xdb9dab0a):
 1(p1): addr:aa:55:aa:55:00:14
     config:     0
     state:      LIVE
     speed: 0 Mbps now, 0 Mbps max
 2(p2): addr:aa:55:aa:55:00:15
     config:     0
     state:      LIVE
     speed: 0 Mbps now, 0 Mbps max
 3(p3): addr:aa:55:aa:55:00:16
     config:     0
     state:      LIVE
     speed: 0 Mbps now, 0 Mbps max
 4(p4): addr:aa:55:aa:55:00:17
     config:     0
     state:      LIVE
     speed: 0 Mbps now, 0 Mbps max
 5(p5): addr:aa:55:aa:55:00:18
     config:     0
     state:      LIVE
     speed: 0 Mbps now, 0 Mbps max
 LOCAL(br0): addr:42:51:a1:c4:97:45
     config:     0
     state:      LIVE
     speed: 0 Mbps now, 0 Mbps max
```

After this bit you should also see the request to delete all existing flows and then start adding new ones.
> Hint: look for the line with actions=drop at the end.

##### OpenFlow Layer
Following up on everything we have done so far, let's look at the OpenFlow tables that Faucet set up. It is helpful to take a look at **docs/architecture.rst** in order to learn how Faucet structures its tables. In summary, when all features are enabled this should be the table layout:


Table 0
> Port-based ACLs

Table 1
> Ingress VLAN processing

Table 2
> VLAN-based ACLs

Table 3
> Ingress L2 processing, MAC learning

Table 4
> L3 forwarding for IPv4

Table 5
> L3 forwarding for IPv6

Table 6
> Virtual IP processing, e.g. for router IP addresses implemented by Faucet

Table 7
> Egress L2 processing

Table 8
> Flooding

With this in mind, let's dump the flow tables. We could do so by running the plain **ovs-ofctl dump-flows** command; However, that would fill our logs with useless data and therefore making it harder to read the output.

> In addition, for historical reasons ovs-ofctl always defaults to using OpenFlow 1.0 even though Faucet and most modern controllers use OpenFlow 1.3, so it’s best to force it to use OpenFlow 1.3.

To facilitate our work, let's define the following functions, which will help us in the future:

```bash
dump-flows () {
  ovs-ofctl -OOpenFlow13 --names --no-stat dump-flows "$@" \
    | sed 's/cookie=0x5adc15c0, //'
}
save-flows () {
  ovs-ofctl -OOpenFlow13 --no-names --sort dump-flows "$@"
}
diff-flows () {
  ovs-ofctl -OOpenFlow13 diff-flows "$@" | sed 's/cookie=0x5adc15c0 //'
}
```

Having done this, we can finally look at the flows we have got by running the following command:

```bash
dump-flows br0
```

Faucet tries to minimize resource utilisation on hardware switches, because of that it will try to install the minimal set of tables to match the features enabled in **faucet.yaml**. Since we only have switching enabled there will only be 4 tables on **faucet.log**, check that out with this command:

```bash
cat faucet.log | grep "table ID"
```

Currently we have:

Table 0 (vlan)
> Ingress VLAN processing

Table 1 (eth_src)
> Ingress L2 processing, MAC learning

Table 2 (eth_dst)
> Egress L2 processing

Table 3 (flood)
> Flooding

The original tutorial has a good theoric explanation on the data in each of the tables, it is recommended to check the [Open vSwitch](https://docs.openvswitch.org/en/latest/tutorials/faucet/#switching) website.

##### Tracing
In order to look at the path a particular packet takes through OVS we can use the **ofproto/trace** command to play "what-if?" games. This command is one that we send directly to **ovs-vswitchd**, using the **ovs-appctl** utility.

> **ovs-appctl** is actually a very simple-minded JSON-RPC client, so you could also use some other utility that speaks JSON-RPC, or access it from a program as an API.

The **ovs-vswitchd**(8) manpage has a lot of detail on how to use **ofproto/trace**. Let's try to do something simple, we will run a command that specifies the datapath (in this case **br0**) and an input port.

```bash
ovs-appctl ofproto/trace br0 in_port=p1
```

> Unspecified fields default to all-zeros.

The first line of output, beginning with Flow:, just repeats our request in a more verbose form, including the L2 fields that were zeroed.

Each of the numbered items under **bridge("br0")** shows what would happen to our hypothetical packet in the table with the given number.

Summary information follows the numbered tables. The packet hasn’t been changed (overall, even though a VLAN was pushed and then popped back off) since ingress, hence **Final flow: unchanged**. We’ll look at the **Megaflow** information later. The **Datapath actions** summarize what would actually happen to such a packet.

##### Trigering MAC Learning
Let's see what happens when we send packet to the controller in order to trigger MAC learning.

Start by running the following command, this will let us have a basis for comparison.
```bash
save-flows br0 > flows1
```

Now we will use **ofproto/trace**, this time, however, we will specify the source and destination Ethernet addresses and append the **-generate** option so that side effects like sending a packet to the controller actually happen.

```bash
ovs-appctl ofproto/trace br0 in_port=p1,dl_src=00:11:11:00:00:00,dl_dst=00:22:22:00:00:00 -generate
```

The output looks almost unchanged, but check what happens **on the faucet side**:

```bash
cat faucet.log | grep learned
```

> We can see that it learnt about our **MAC 00:11:11:00:00:00**.

Let's now compare the flow tables that we saved to the current ones:

```bash
diff-flows flows1 br0
```

> We can see the new flows for the learned MAC addresses.

Now, if we run the following command we will be able to understand the usefulness of the learnt MAC.
```bash
ovs-appctl ofproto/trace br0 in_port=p2,dl_src=00:22:22:00:00:00,dl_dst=00:11:11:00:00:00 -generate
```
The first time you run this commnad the packet will be sent to the controller, allowing it to learn p2's MAC address. Afterwards, if we look at the **faucet.log** we can confirm it.

```bash
cat faucet.log | grep learned
```

> It is also noticeable with **diff-flows**, run ```diff-flows flows1 br0```

Now, if we run the **ofproto/trace** commands, we will see the packets go back and forth without any further MAC learning.

##### Performance
Open vSwitch has a concept of a "fast path" and a "slow path"; ideally all packets stay in the fast path. We do need, however, both this paths to ensure that OVS performs as fast as possible.

The **Open vSwitch code is divided into two major components** which, as already mentioned, are called the “slow path” and “fast path” (aka “datapath”). The **slow path is embedded in the ovs-vswitchd userspace program**. It is the part of the Open vSwitch packet processing logic that understands OpenFlow. **Its job is to take a packet and run it through the OpenFlow tables to determine what should happen to it**. It outputs a list of actions in a form similar to OpenFlow actions but simpler, called “ODP actions” or “datapath actions”. It then passes the ODP actions to the datapath, which applies them to the packet.

> Open vSwitch contains a single slow path and multiple fast paths. 

The **key to** getting **high performance** from this architecture **is caching**.

Open vSwitch includes a multi-level cache that works as follows:

1. **Microflow cache**: key to performance for relatively long-lived, high packet rate flows. If the datapath has a microflow cache, then it consults it and, if there is a cache hit, the datapath executes the associated actions. Otherwise, it proceeds to step 2.
2. **Megaflow cache**: key to performance for shorter or low packet rate flows. If there is a megaflow cache hit, the datapath executes the associated actions. Otherwise, it proceeds to step 3.
3. The datapath passes the packet to the slow path, which runs it through the OpenFlow table to yield ODP actions, a process that is often called “**flow translation**”. It then passes the packet back to the datapath to execute the actions and to, if possible, install a megaflow cache entry so that subsequent similar packets can be handled directly by the fast path. (We already described above most of the cases where a cache entry cannot be installed.)

The **megaflow cache is the key cache to consider for performance tuning**. Open vSwitch provides tools for understanding and optimizing its behavior. The **ofproto/trace** command that we have already been using is the most common tool for this use. Let’s take another look at the most recent **ofproto/trace** output:

```bash
ovs-appctl ofproto/trace br0 in_port=p2,dl_src=00:22:22:00:00:00,dl_dst=00:11:11:00:00:00 -generate
```

We are interested in the last line. It shows the entry that OVS would insert into the megaflow cache given the particular packet with the current flow tables.

- recirc_id is not something the user normally needs to understand 
- **eth**:  This just indicates that the cache entry matches only Ethernet packets (Open vSwitch also supports other types of packets)
- All of the fields matched by any of the flows that the packet visited:
    > **in_port**: In tables 0 and 1.

    > **vlan_tci**: In tables 0, 1, and 2.

    > **dl_src**: In table 1.

    > **dl_dst**: In table 2.
- All of the fields matched by flows that had to be ruled out to ensure that the ones that actually matched were the highest priority matching rules.

The last one is important. Notice how the megaflow matches on **dl_type=0x0000**, even though none of the tables matched on **dl_type** (the Ethernet type). One reason is because of this flow in OpenFlow table 1 (which shows up in **dump-flows** output):
```bash
table=1, priority=9099,dl_type=0x9000 actions=drop
```

#### Routing
Let's now start over, adding a L3 routing into the picture. To do this, we just need to change our **vlans** section in **inst/faucet.yaml** to specify a router IP address for each VLAN and define a router between them.

```yaml
dps:
    switch-1:
        dp_id: 0x1
        timeout: 11800
        arp_neighbor_timeout: 3600
        interfaces:
            1:
                native_vlan: 100
            2:
                native_vlan: 100
            3:
                native_vlan: 100
            4:
                native_vlan: 200
            5:
                native_vlan: 200
vlans:
    100:
        faucet_vips: ["10.100.0.254/24"]
    200:
        faucet_vips: ["10.200.0.254/24"]
routers:
    router-1:
        vlans: [100, 200]
```
After changing the configuration file, run:
```bash
sudo docker exec faucet pkill -HUP -f faucet.faucet
```
You can now check the tables with:
```bash
cat faucet.log | grep "table config"
```


#### ACLs
#### Finishing Up