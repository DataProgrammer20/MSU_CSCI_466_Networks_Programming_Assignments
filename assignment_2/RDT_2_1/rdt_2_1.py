import argparse
import hashlib
from time import sleep
from time import time

from assignment_2.RDT_2_1 import network_2_1


class Packet:
    # the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    # length of md5 checksum in hex
    checksum_length = 32

    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S

    @classmethod
    def from_byte_S(self, byte_S):
        if Packet.corrupt(byte_S):
            raise RuntimeError('Cannot initialize Packet: byte_S is corrupt')
        # extract the fields
        seq_num = int(byte_S[Packet.length_S_length: Packet.length_S_length + Packet.seq_num_S_length])
        msg_S = byte_S[Packet.length_S_length + Packet.seq_num_S_length + Packet.checksum_length:]
        return self(seq_num, msg_S)

    def get_byte_S(self):
        # convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        # convert length to a byte field of length_S_length bytes
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S)).zfill(
            self.length_S_length)
        # compute the checksum
        checksum = hashlib.md5((length_S + seq_num_S + self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        # compile into a string
        return length_S + seq_num_S + checksum_S + self.msg_S

    @staticmethod
    def corrupt(byte_S):
        # extract the fields
        length_S = byte_S[0:Packet.length_S_length]
        seq_num_S = byte_S[Packet.length_S_length: Packet.seq_num_S_length + Packet.seq_num_S_length]
        checksum_S = byte_S[
                     Packet.seq_num_S_length + Packet.seq_num_S_length: Packet.seq_num_S_length + Packet.length_S_length + Packet.checksum_length]
        msg_S = byte_S[Packet.seq_num_S_length + Packet.seq_num_S_length + Packet.checksum_length:]

        # compute the checksum locally
        checksum = hashlib.md5(str(length_S + seq_num_S + msg_S).encode('utf-8'))
        computed_checksum_S = checksum.hexdigest()
        # and check if the same
        return checksum_S != computed_checksum_S


class RDT:
    # latest sequence number used in a packet
    seq_num = 1
    seq_num_received = 1
    # buffer of bytes read from network
    byte_buffer = ''
    duplicate = False

    def __init__(self, role_S, server_S, port):
        self.network = network_2_1.NetworkLayer(role_S, server_S, port)

    def disconnect(self):
        self.network.disconnect()

    def rdt_1_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())

    def rdt_1_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        # keep extracting packets - if reordered, could get more than one
        while True:
            # check if we have received enough bytes
            if len(self.byte_buffer) < Packet.length_S_length:
                return ret_S  # not enough bytes to read packet length
            # extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S  # not enough bytes to read the whole packet
            # create packet from buffer content and add to return string
            p = Packet.from_byte_S(self.byte_buffer[0:length])
            ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
            # remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            # if this was the last packet, will return on the next iteration

    # RDT_2_1 sending function
    def rdt_2_1_send(self, msg_S):
        # First, create a new packet and send it over the network
        packet = Packet(self.seq_num, msg_S)
        self.network.udt_send(packet.get_byte_S())
        # Continue to receive bytes over the network

        packet_bytes = self.network.udt_receive()
        self.byte_buffer += packet_bytes

        # Infinite loop is ooccuring here. byte_buffer is not receiving packets

        while True:
            print("Help me! I'm stuck!!!!")
            # This is the infinite loop location

            packet_bytes = self.network.udt_receive()
            self.byte_buffer += packet_bytes
            # Check if we have received enough packet bytes
            if len(self.byte_buffer) >= packet.length_S_length:
                # Extract the length of the packet
                length = int(self.byte_buffer[:packet.length_S_length])
                # Check if we have enough bytes to read the whole packet
                if len(self.byte_buffer) >= length:
                    # If so, check if the packet is corrupted
                    if Packet.corrupt(self.byte_buffer[0:length]):
                        # Remove bytes from corrupted packet, resend packet bytes
                        self.byte_buffer = self.byte_buffer[length:]
                        self.network.udt_send(packet.get_byte_S())
                    else:
                        # Else, packet is not corrupt
                        received_packet = packet.from_byte_S(self.byte_buffer[0:length])
                        # Remove current packet bytes from buffer
                        self.byte_buffer = self.byte_buffer[length:]
                        # Check if packet is ACK
                        if received_packet.msg_S == 'ACK' and received_packet.seq_num >= self.seq_num:
                            # If so, increment the sequence number
                            self.seq_num += 1
                            return
                        else:
                            # Else, resend the packet bytes
                            self.network.udt_send(packet.get_byte_S())

    # RDT_2_1 receiving function
    def rdt_2_1_receive(self):
        ret_S = None
        packet_bytes = self.network.udt_receive()
        self.byte_buffer += packet_bytes
        while True:
            # Check if we have received enough bytes
            if len(self.byte_buffer) < Packet.length_S_length:
                # Not enough bytes to read packet length
                return ret_S
            # Extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                # Not enough bytes to read whole packet
                return ret_S
            # check for packet corruption?
            if Packet.corrupt(self.byte_buffer[0:length]):
                # The packet is corrupt, so send NAK
                nak = Packet(self.seq_num_received, 'NAK')
                self.network.udt_send(nak.get_byte_S())
                self.byte_buffer = self.byte_buffer[length:]
            else:
                # Create packet from buffer content
                packet = Packet.from_byte_S(self.byte_buffer[0:length])
                if packet.seq_num == self.seq_num_received:
                    # If the packet is not corrupted and has the correct sequence number send ACK
                    ret_S = packet.msg_S if (ret_S is None) else ret_S + packet.msg_S
                    self.seq_num_received += 1
                    ack = Packet(self.seq_num, 'ACK')
                    self.network.udt_send(ack.get_byte_S())
                    # Set timer, wait for more packets from sender
                    timer = time() + 2.0
                    # Create new receiver byte buffer
                    receiver_byte_buffer = ''
                    while time() < timer:
                        receiver_bytes = self.network.udt_receive()
                        receiver_byte_buffer += receiver_bytes
                        # Now we just do what we have already done
                        if len(receiver_byte_buffer) < Packet.length_S_length:
                            # Continue if we have not received enough bytes
                            continue
                        length = int(receiver_byte_buffer[:Packet.length_S_length])
                        if len(receiver_byte_buffer) < length:
                            # Continue if we do not have enough bytes to read the packet
                            continue
                        if Packet.corrupt(receiver_byte_buffer[0:length]):
                            # Send NAK, clear buffer
                            nak = Packet(self.seq_num_received, 'NAK')
                            self.network.udt_send(nak.get_byte_S())
                            receiver_byte_buffer = ''
                            # Check if it was a duplicate
                            if self.duplicate:
                                # Increment timer
                                timer += 2.0
                            continue
                        # Else, packet is not corrupt
                        else:
                            received_packet = Packet.from_byte_S(receiver_byte_buffer[0:length])
                            # Check if packet sequence number is a duplicate, indicating duplicate packet
                            if received_packet.seq_num == self.seq_num_received - 1:
                                self.duplicate = True
                                # Increment timer
                                timer += 2.0
                                # ACK the duplicate packet again
                                self.network.udt_send(ack.get_byte_S())
                                # Clear receiver byte buffer
                                receiver_byte_buffer = ''
                            else:
                                # Else, send a NAK
                                nak = Packet(self.seq_num_received, 'NAK')
                                self.network.udt_send(nak.get_byte_S())
                                # Break from while loop
                                break
            # Finally, remove packet bytes from buffer
            self.byte_buffer = self.byte_buffer[length:]

    def rdt_3_0_send(self, msg_S):
        pass

    def rdt_3_0_receive(self):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        rdt.rdt_2_1_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_2_1_receive())
        rdt.disconnect()
    else:
        sleep(1)
        print(rdt.rdt_2_1_receive())
        rdt.rdt_2_1_send('MSG_FROM_SERVER')
        rdt.disconnect()
