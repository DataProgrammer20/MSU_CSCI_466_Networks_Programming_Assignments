"""
Created on Oct 12, 2016
@author: mwittie
"""
import queue
import threading


# wrapper class for a queue of packets
class Interface:
    # @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize)
        self.mtu = None

    # get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None

    # put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)


# Implements a network layer packet (different from the RDT packet
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    # packet encoding lengths
    dst_addr_S_length = 5
    header_length = 1

    # @param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, data_S, flag=0, offset=0):
        self.dst_addr = dst_addr
        self.data_S = data_S
        # new variables for part 2
        self.frg_flag = flag
        self.frg_offset = offset
        self.frg_flag_length = 1
        self.frg_offset_length = 2
        self.header_length = self.dst_addr_S_length + self.frg_flag_length + self.frg_offset_length

    # called when printing the object
    def __str__(self):
        return self.to_byte_S()

    # convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += self.data_S
        return byte_S

    # extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[0: NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length:]
        return self(dst_addr, data_S)

    # The fragmentize function constructs the fragmented packet
    def fragmentize(self):
        byte = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte += str(self.frg_flag).zfill(self.frg_flag_length)
        byte += str(self.frg_offset).zfill(self.frg_offset_length)
        byte += self.data_S
        return byte

    # Extracts the fragmented packet
    @classmethod
    def extract_fragment_byte(self, byte, mtu):
        dst_addr = int(byte[0:NetworkPacket.dst_addr_S_length])
        byte_data = byte[NetworkPacket.dst_addr_S_length:]
        frag_packets = []
        offset = 0
        flag = 2

        while True:
            if self.header_length + len(byte_data[offset:]) > mtu:
                flag = 1
            else:
                flag = 0

            increment = mtu + offset - self.header_length

            frag_packets.append(NetworkPacket(dst_addr, byte_data[offset:increment], flag, offset))
            offset = increment

            if flag == 0:
                break
            # if flag == 2:
            # More code might be needed here
        return frag_packets


# Implements a network host for receiving and transmitting data
class Host:
    # @param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False  # for thread termination
        self.fragments = []

    # called when printing the object
    def __str__(self):
        return 'Host_%s' % self.addr

    # create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S, limit):
        # Check if the length of the data is greater than the limit
        if len(data_S) > limit:
            # If the length of the data is greater, continue
            f_char = 0
            l_char = limit
            while True:
                # If the l_char is greater than the length of the data_S, create the network packet
                # and put it into the out-bound interface.
                if l_char > len(data_S):
                    packet = NetworkPacket(dst_addr, data_S[f_char:])
                    self.out_intf_L[0].put(packet.to_byte_S())
                    print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, packet, self.out_intf_L[0].mtu))
                    break
                # Else, segment the data into a new network packet, and put it into the out-bound interface
                else:
                    packet = NetworkPacket(dst_addr, data_S[f_char:l_char])
                    self.out_intf_L[0].put(packet.to_byte_S())
                # Increment both f_char and l_char with the limit
                f_char += limit
                l_char += limit
                print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, packet, self.out_intf_L[0].mtu))
        # Else, we can create the network packet and put it into the out-bound interface
        else:
            packet = NetworkPacket(dst_addr, data_S)
            self.out_intf_L[0].put(packet.to_byte_S())
            print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, packet, self.out_intf_L[0].mtu))

    # receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        if pkt_S is not None:
            self.fragments.append(pkt_S[NetworkPacket.header_length:])
            if pkt_S[NetworkPacket.dst_addr_S_length] == 0:
                print('%s: received packet "%s" on the in interface' % (self, pkt_S))
                self.fragments = []

    # thread target for the host to keep receiving data
    def run(self):
        print(threading.currentThread().getName() + ': Starting')
        while True:
            # receive data arriving to the in interface
            self.udt_receive()
            # terminate
            if self.stop:
                print(threading.currentThread().getName() + ': Ending')
                return


# Implements a multi-interface router described in class
class Router:
    # @param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size):
        self.stop = False  # for thread termination
        self.name = name
        # create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    # called when printing the object
    def __str__(self):
        return 'Router_%s' % self.name

    # look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                # get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                # if packet exists make a forwarding decision
                if pkt_S is not None:
                    p = NetworkPacket.extract_fragment_byte(pkt_S, self.out_intf_L[i].mtu)  # parse a packet out
                    # Forward fragments
                    for packet_number in p:
                        self.out_intf_L[i].put(packet_number.fragmentize(), True)
                        print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                        % (self, p, i, i, self.out_intf_L[i].mtu))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass

    # thread target for the host to keep forwarding data
    def run(self):
        print(threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print(threading.currentThread().getName() + ': Ending')
                return
