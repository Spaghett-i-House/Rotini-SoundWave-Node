import struct
import enum

RTPVERSION = 2
MAXPACKETSIZE = 1518
import wave



class RTPPacket(object):

    def __init__(self, version=RTPVERSION, padding=0, extension=0, marker=0, payload_type=0,
                 sequence_number=0, timestamp=0, ssrc=0, csrc_list=[]):

        if padding > 1:
            raise(AssertionError("Padding has a range of 0 of 1"))
        if extension > 0:
            raise(AssertionError("extension has a range of 0 or 1"))
        if marker > 0:
            raise(AssertionError("Marker has a range of 0 or 1"))
        #print(csrc_list, type(csrc_list))
        self.version = version
        self.padding = padding
        self.extension = extension
        self.marker = marker
        self.payload_type = payload_type
        self.sequence_number = sequence_number
        self.timestamp = timestamp
        self.ssrc = ssrc
        self.csrc_list = csrc_list
        self.csrc_len = len(csrc_list)
        self.data_bytes = None
        self.total_length = 12 + 4*self.csrc_len

    def set_data_bytes(self, data_bytes: bytes) -> bytes:
        """available_length = MAXPACKETSIZE - self.total_length
        chopped_data = data_bytes[0:]
        self.data_bytes = chopped_data
        print(len(self.data_bytes))
        wf.writeframes(self.data_bytes)
        return chopped_data[available_length:]"""
        self.data_bytes = data_bytes

    def serialize(self) -> bytes:
        byte_1 = (self.version << 6) | (self.padding << 5) | (self.extension << 4) | self.csrc_len
        #print(bin(byte_1))
        byte_2 = (self.marker << 7) | self.payload_type
        if self.csrc_len == 0:
            if self.data_bytes is None:
                return struct.pack("!BBhfI", byte_1, byte_2, self.sequence_number,
                                   self.timestamp, self.ssrc)
            else:
                return struct.pack("!BBhfI{}b".format(len(self.data_bytes)), byte_1, byte_2, self.sequence_number,
                                   self.timestamp, self.ssrc, self.data_bytes)
        else:
            if self.data_bytes is None:
                return struct.pack("!BBhfI{}I".format(self.csrc_len), byte_1, byte_2, self.sequence_number,
                                   self.timestamp, self.ssrc, *self.csrc_list)
            else:
               #self.print()
                return struct.pack("!BBhfI{}I{}s".format(self.csrc_len, len(self.data_bytes)),
                                   byte_1,
                                   byte_2,
                                   self.sequence_number,
                                   self.timestamp,
                                   self.ssrc,
                                   *self.csrc_list,
                                   self.data_bytes)

    def print(self) -> None:
        print("""
        RTPPACKET:
        - Version: {}
        - padding: {}
        - extension: {}
        - marker: {}
        - ssrc: {}
        """.format(self.version,
                   self.padding,
                   self.extension,
                   self.marker,
                   self.payload_type,
                   self.sequence_number,
                   self.ssrc), end="")
        print("- timestamp:", self.timestamp)
        print("     - csrc-l", self.csrc_list)
        print("     - data", self.data_bytes)


def decode_rtp(message: bytes) -> RTPPacket:
    # version 2 bits
    # padding 1 bit
    # extension 1 bit
    # csrccount 4 bits end of byte 1
    first_byte = message[0]
    version = (first_byte & 0b11000000) >> 6
    padding = (first_byte & 0b00100000) >> 5
    extension = (first_byte & 0b00010000) >> 4
    csrccount = (first_byte & 0b00001111)

    # marker 1 bit
    # payload_type 7 bits, end of byte 2
    second_byte = message[1]
    marker = (second_byte & 0b10000000) >> 7
    payload_type = (second_byte & 0b01111111)

    rest_of_header = message[2:]
    # sequence_number 16 bits: short
    # timestamp 32 bits: int
    # ssrc 32 bits: int
    # csrc list 32 bits each from csrccount
    data_length = len(rest_of_header) - 10 - csrccount*4
    if csrccount > 0:
        (seq_num, timestamp, ssrc, csrc_list, data) = struct.unpack('!hfI{}I{}s'.format(csrccount, data_length),
                                                                    rest_of_header)
        if csrccount == 1:
            csrc_list = [csrc_list]
    else:
        (seq_num, timestamp, ssrc, data) = struct.unpack('!hfI{}s'.format(data_length), rest_of_header)
        csrc_list = []
    new_rtp_packet = RTPPacket(version=version, padding=padding, extension=extension, marker=marker,
                               payload_type=payload_type, sequence_number=seq_num, timestamp=timestamp,
                               ssrc=ssrc, csrc_list=csrc_list)
    new_rtp_packet.set_data_bytes(data)
    return new_rtp_packet


class RTPPayloadType(enum.Enum):
    UINT8 = 0,
    SHORT = 1,
    INT32 = 2,
    FLOAT32 = 3

"""rtppack = RTPPacket(padding=1, payload_type=10)
rtppack.set_data_bytes(b'x02x03x04')
rtppack.print()
nrtppack = decode_rtp(rtppack.serialize())
nrtppack.print()"""
