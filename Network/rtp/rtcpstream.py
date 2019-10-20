import socket
import soundcard as sc
import time
import numpy as np
from queue import Queue, Full, Empty
from threading import Thread
from Network.rtp.rtcppacket import RTCPPacket, decode_rtcp, RTCPPacketType
from Network.rtp.rtpstream import RTPStream

class RTCPStream(object):

    def __init__(self, remote_endpoint: (str, int), rtp_stream: RTPStream, ssrc: int):
        # set control variables
        self.close_flag = False
        self.rtp_stream = rtp_stream  # the stream to get statistics from and such

        # create socket for transfers
        self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind socket to rtp stream port +1 as protocol specifies
        self.sockfd.bind(("", rtp_stream.get_address()[1] + 1))  # [0] is addr [1] is port from get address

        # create variables to be externally accessed
        self.address = self.sockfd.getsockname()
        self.endpoint = remote_endpoint
        self.ssrc = ssrc
        # create queues for multithreading
        self.packet_out_queue = Queue(maxsize=5)  # setting maxsize allows us to skip bytes if we are too slow
        self.packet_in_queue = Queue(maxsize=5)

        # start threads for output
        self.network_output_thread = Thread(target=self.send_outgoing_packets_thread)
        self.network_output_thread.start()

        # start threads for input (rtp is bidirectional)
        self.network_input_queue = Thread(target=self.read_incoming_packets_thread)
        self.network_input_queue.start()

    def read_incoming_packets_thread(self):
        while not self.close_flag:
            in_packet, r_address = self.sockfd.recvfrom(16000)
            in_as_rtpc = decode_rtcp(in_packet)
            in_as_rtpc.print()
            packet_type_as_enum = RTCPPacketType(in_as_rtpc.packet_type)
            switch = {
                RTCPPacketType.SOURCE_DESCRIPTION: print,
                RTCPPacketType.RECEIVER_REPORT: print,
                RTCPPacketType.SENDER_REPORT: print,
                RTCPPacketType.GOODBYE: self.on_goodbye,
                RTCPPacketType.APP: print
            }
            function = switch.get(packet_type_as_enum, lambda: "[WARNING]Invalid packet type received")
            f_return = function(in_as_rtpc)
            #TODO Handle sender report
            #TODO Handle Receiver Report
            #TODO Handle Source Description
            #TODO Handle Goodbye
            #TODO Handle APP

    def send_outgoing_packets_thread(self):
        while not self.close_flag:
            try:
                # get data to send
                rtcp_packet: RTCPPacket = self.packet_out_queue.get(timeout=1)
                self.sockfd.sendto(rtcp_packet.serialize(), self.endpoint)
            except Empty:
                print("[WARNING] no outgoing packets found")
                continue

    def send_goodbye(self) -> None:
        # I would like to send a goodbye
        goodbye_packet = RTCPPacket(packet_type=RTCPPacketType.GOODBYE.value, ssrc=self.ssrc)
        self.packet_out_queue.put(goodbye_packet)
        print("[STATUS] BYE added to queue")
        self.rtp_stream.close()

    def on_goodbye(self, received_packet: RTCPPacket) -> None:
        # I got a goodbye from other member
        print("[STATUS] BYE Received")
        self.rtp_stream.close()
        self.close()
        print("[STATUS] Session closed on BYE")

    def close(self) -> None:
        self.close_flag = True
        if self.network_output_thread.is_alive():
            self.network_output_thread.join()
        if self.netis_alive():
            self.audio_input_thread.join()

        self.sockfd.close()
        print("[STATUS] RTP Stream has been closed")

