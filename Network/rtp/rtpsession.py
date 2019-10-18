from Network.rtp.rtcppacket import RTCPPacket, decode_rtcp
from Network.rtp.rtppacket import RTPPacket, decode_rtp, RTPPayloadType
import socket
from queue import Queue, Empty
import time
from threading import Thread
import struct
import wave

class RTPSession(object):

    def __init__(self, data_addr: (str, int), control_addr: (str, int), sessionID: int,
                 start_sequence_number, onEndCallback: callable):
        self.close_flag = False
        self.session_id = sessionID
        self.data_addr = data_addr
        self.control_addr = control_addr
        self.onEndCallback = onEndCallback
        self.sequence_number = start_sequence_number

        self.controlfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.controlfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.controlfd.bind(("", 0))
        self.controlfd.settimeout(1)

        self.datafd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.datafd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.datafd.bind(("", 0))
        self.datafd.settimeout(1)

        self.rtp_data_queue = Queue(maxsize=5)

        self.rtcp_read_thread = Thread(target=self.monitor_control)
        self.rtcp_read_thread.start()
        self.rtp_read_thread = Thread(target=self.monitor_data)
        self.rtp_read_thread.start()
        self.rtp_write_thread = Thread(target=self.send_stream)
        self.rtp_write_thread.start()
        print("New RTP Session started {} with data on {} and control on {}".format(sessionID,
                                                                                    self.datafd.getsockname()[1],
                                                                                    self.controlfd.getsockname()[1]))
        self.send_initial_app_address()

    def send_initial_app_address(self):
        new_rtcp_msg = RTCPPacket(packet_type=4, ssrc=self.session_id)  # application specific message
        data_addr = self.datafd.getsockname()
        control_addr = self.controlfd.getsockname()
        # data addr, data port, control addr, control_port
        addr_data = struct.pack("!iiii",
                                struct.unpack("!i", socket.inet_aton(data_addr[0]))[0],
                                data_addr[1],
                                struct.unpack("!i", socket.inet_aton(control_addr[0]))[0],
                                control_addr[1])
        new_rtcp_msg.add_data(addr_data)
        self.controlfd.sendto(new_rtcp_msg.serialize(), self.control_addr)

    def monitor_control(self):
        while not self.close_flag:
            try:
                recvd_rtcp, recvd_addr = self.controlfd.recvfrom(1024)
                rtcp_decoded = decode_rtcp(recvd_rtcp)
                rtcp_decoded.print()
            except socket.timeout as err:
                continue

    def monitor_data(self):
        while not self.close_flag:
            try:
                recvd_rtp, recvd_addr = self.datafd.recvfrom(1024)
                rtp_decoded = decode_rtp(recvd_rtp)
                rtp_decoded.print()
            except socket.timeout as err:
                continue

    def send_stream(self):
        while not self.close_flag:
            try:
                (rtp_data, csrc, data_type, data_timestamp) = self.rtp_data_queue.get(timeout=1)
                rtp_packet = RTPPacket(payload_type=data_type, sequence_number=self.sequence_number,
                                       timestamp=data_timestamp, ssrc=self.session_id, csrc_list=[csrc])
                rtp_packet.set_data_bytes(rtp_data)
                self.sequence_number += 1
                self.datafd.sendto(rtp_packet.serialize(), self.data_addr)
            except Empty:
                #print("No audio data")
                continue

    def add_data_to_stream(self, data_bytes: bytes, data_csrc: int, data_type: RTPPayloadType, data_timestamp: float):
        self.rtp_data_queue.put((data_bytes, data_csrc, int(data_type.value[0]), data_timestamp))

    def close(self):
        # set close flag
        self.close = True
        # wait for threads to stop
        self.rtp_write_thread.join()
        self.rtcp_read_thread.join()
        self.rtp_read_thread.join()
        # close sockets
        self.datafd.close()
        self.controlfd.close()
        print("RTP Session {} has closed".format(self.session_id))
        self.onEndCallback(self.session_id)


