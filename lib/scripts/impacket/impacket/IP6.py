
from ImpactPacket import Header
from IP6_Address import IP6_Address

import struct
import array

class IP6(Header):
    #Ethertype value for IPv6
    ethertype = 0x86DD
    HEADER_SIZE = 40
    IP_PROTOCOL_VERSION = 6
    
    def __init__(self, buffer = None):
        Header.__init__(self, IP6.HEADER_SIZE)
        self.set_protocol_version(IP6.IP_PROTOCOL_VERSION)
        if (buffer):
            self.load_header(buffer)
        
    
    def get_header_size(self):
        return IP6.HEADER_SIZE

    def __str__(self):        
        protocol_version = self.get_protocol_version()
        traffic_class = self.get_traffic_class()
        flow_label = self.get_flow_label()
        payload_length = self.get_payload_length()
        next_header = self.get_next_header()
        hop_limit = self.get_hop_limit()
        source_address = self.get_source_address()
        destination_address = self.get_destination_address()

        s = "Protocol version: " + str(protocol_version) + "\n"
        s += "Traffic class: " + str(traffic_class) + "\n"
        s += "Flow label: " + str(flow_label) + "\n"
        s += "Payload length: " + str(payload_length) + "\n"
        s += "Next header: " + str(next_header) + "\n"
        s += "Hop limit: " + str(hop_limit) + "\n"
        s += "Source address: " + source_address.as_string() + "\n"
        s += "Destination address: " + destination_address.as_string() + "\n"
        return s
    
    def get_pseudo_header(self):
        source_address = self.get_source_address().as_bytes()
        #FIXME - Handle Routing header special case
        destination_address = self.get_destination_address().as_bytes()
        #FIXME - Check if upper-layer protocol has a packet length field
        #Else, compute it from the payload length subtracting the extension headers length
        upper_layer_packet_length = struct.pack('!L', self.get_payload_length())
        reserved_bytes = [ 0x00, 0x00, 0x00 ]
        #FIXME - If there are extension headers, fetch the correct upper-player protocol number by traversing the list
        upper_layer_protocol_number = struct.pack('B', self.get_next_header())
        
        
        pseudo_header = array.array('B')        
        pseudo_header.extend(source_address)
        pseudo_header.extend(destination_address)
        pseudo_header.fromstring(upper_layer_packet_length)
        pseudo_header.fromlist(reserved_bytes)
        pseudo_header.fromstring(upper_layer_protocol_number)
        return pseudo_header
    
############################################################################
    def get_protocol_version(self):
        return (self.get_byte(0) & 0xF0) >> 4

    def get_traffic_class(self):
        return ((self.get_byte(0) & 0x0F) << 4) | ((self.get_byte(1) & 0xF0) >> 4)

    def get_flow_label(self):
        return (self.get_byte(1) & 0x0F) << 16 | (self.get_byte(2) << 8) | self.get_byte(3)

    def get_payload_length(self):
        return (self.get_byte(4) << 8) | self.get_byte(5)

    def get_next_header(self):
        return (self.get_byte(6))

    def get_hop_limit(self):
        return (self.get_byte(7))

    def get_source_address(self):
        address = IP6_Address(self.get_bytes()[8:24])
        return (address)    

    def get_destination_address(self):
        address = IP6_Address(self.get_bytes()[24:40])
        return (address)    

############################################################################
    def set_protocol_version(self, version):
        if (version != 6):
            raise Exception('set_protocol_version - version != 6')
    
        #Fetch byte, clear high nibble
        b = self.get_byte(0) & 0x0F
        #Store version number in high nibble
        b |= (version << 4)
        #Store byte in buffer
        #This behaviour is repeated in the rest of the methods 
        self.set_byte(0, b)


    def set_traffic_class(self, traffic_class):
        b0 = self.get_byte(0) & 0xF0
        b1 = self.get_byte(1) & 0x0F
        b0 |= (traffic_class & 0xF0) >> 4
        b1 |= (traffic_class & 0x0F) << 4
        self.set_byte(0, b0)
        self.set_byte(1, b1)
    

    def set_flow_label(self, flow_label):
        b1 = self.get_byte(1) & 0xF0
        b1 |= (flow_label & 0xF0000) >> 16
        self.set_byte(1, b1)
        self.set_byte(2, (flow_label & 0x0FF00) >> 8)
        self.set_byte(3, (flow_label & 0x000FF))
 

    def set_payload_length(self, payload_length):
        self.set_byte(4, (payload_length & 0xFF00) >> 8)
        self.set_byte(5, (payload_length & 0x00FF))
    

    def set_next_header(self, next_header):
        self.set_byte(6, next_header)
    
    def set_hop_limit(self, hop_limit):
        self.set_byte(7, hop_limit)
    
    def set_source_address(self, source_address):
        address = IP6_Address(source_address)
        bytes = self.get_bytes()
        bytes[8:24] = address.as_bytes()
        self.set_bytes(bytes)

    def set_destination_address(self, destination_address):
        address = IP6_Address(destination_address)
        bytes = self.get_bytes()
        bytes[24:40] = address.as_bytes()
        self.set_bytes(bytes)

    