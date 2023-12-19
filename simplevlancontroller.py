from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()



class Switch (object):
  """
  A Switch object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

    # Use this table to keep track of which ethernet address is on
    # which switch port (keys are MACs, values are ports).
    self.mac_to_port = {}
    self.vlan_ports = {}
    self.vlan_ports[100] = [1,2]
    self.vlan_ports[200] = [3,4]
    self.vlan_ports[300] = [5,6]

  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)

    # Note that if we didn't get a valid buffer_id, a slightly better
    # implementation would check that we got the full data before
    # sending it (len(packet_in.data) should be == packet_in.total_len)).


  def act_like_switch (self, packet, packet_in):
    """
    Implement switch-like behavior.
    """

    # Learn the port for the source MAC
    self.mac_to_port[packet.src] = packet_in.in_port

    # Get the VLAN for the port
    v = None
    for vlan in self.vlan_ports.keys():
      if packet_in.in_port in self.vlan_ports[vlan]:
        v = vlan

    out_port = None
    if packet.dst in self.mac_to_port.keys():
      ## Send packet out the associated port
      out_port = self.mac_to_port[packet.dst]

      if out_port in self.vlan_ports[v]:
        self.resend_packet(packet_in, out_port)

        log.debug("Installing flow: src = {}, dst = {}, port = {}".format(packet.src, packet.dst, out_port))

        msg = of.ofp_flow_mod()
        
        msg.match = of.ofp_match.from_packet(packet)
        
        action = of.ofp_action_output(port = out_port)
        msg.actions.append(action)
        self.connection.send(msg)

    else:
      for p in self.vlan_ports[v]:
        self.resend_packet(packet_in, p)



  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.

    self.act_like_switch(packet, packet_in)



def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Switch(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
