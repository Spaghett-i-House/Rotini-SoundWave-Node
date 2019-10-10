import struct


class Message(object):

    def __init__(self, message_bytes: bytes, received_address: (str, int)):
        nonhead_len = len(message_bytes)-8
        if len(message_bytes) < 8:
            raise(AssertionError("Message is to short to be valid"))
        (self.opcode,
         self.message_len,
         self.message_id,
         self.body) = struct.unpack("!hhI{}s".format(nonhead_len), message_bytes)
        print(self.opcode, self.message_len, self.message_id, self.body)
        self.received_address = received_address

    def get_opcode(self):
        return self.opcode

    def get_body(self):
        return self.body

    def get_body_len(self):
        return self.message_len

    def get_id(self):
        return self.id
