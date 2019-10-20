import struct
import enum


RTCPVERSION = 2


class RTCPPacket(object):

    def __init__(self, version=RTCPVERSION, padding=0, reception_count=0, packet_type=0, ssrc=0):
        self.version = version
        self.padding = padding
        self.rc = reception_count
        self.packet_type = packet_type
        self.length = 0
        self.ssrc = ssrc
        self.data = None

    def add_data(self, data: bytes) -> None:
        self.data = data
        self.length = len(data)

    def print(self):
        print("""
        RTCPPacket:
        - version: {}
        - padding: {}
        - reception_count: {}
        - packet_type: {}
        - length: {}
        - ssrc: {}
        """.format(self.version,
                   self.padding,
                   self.rc,
                   self.packet_type,
                   self.length,
                   self.ssrc), end="")
        print("- data:", self.data)

    def serialize(self) -> bytes:
        """
        first byte:
        - version 2 bits
        - padding 1 bit
        - reception_report_count 5 bits
        second byte = packet type (char)
        third/fourth byte = length (short)
        4-8th byte: ssrc (int32)
        """
        first_byte = (self.version << 6) | (self.padding << 5) | self.rc
        if self.data:
            return struct.pack("!BBHI{}s".format(self.length), first_byte, self.packet_type, self.length,
                               self.ssrc, self.data)
        else:
            return struct.pack("!BBHI", first_byte, self.packet_type, self.length, self.ssrc)


def decode_rtcp(message: bytes) -> RTCPPacket:
    first_byte = message[0]
    version = (first_byte & 0b11000000) >> 6
    padding = (first_byte & 0b00100000) >> 5
    rec_cou = first_byte & 0b00011111

    packet_type = message[1]
    (data_length, ssrc) = struct.unpack("!HI", message[2:8])
    new_rtcp = RTCPPacket(version, padding, rec_cou, packet_type, ssrc)
    if data_length > 0:
        data = message[8:]
        new_rtcp.add_data(data)
    return new_rtcp


class RTCPPacketType(enum):
    SENDER_REPORT = 0
    RECEIVER_REPORT = 1
    SOURCE_DESCRIPTION = 2
    GOODBYE = 3
    APP = 4
