from Network.Messages.MessageWithResponse import MessageWithResponse
from Network.Messages.Message import Message
from Audio.AudioInputStreamPyaudio import AudioInputStream
import pyaudio
import json
import struct


class InfoMessage(MessageWithResponse):

    def __init__(self, message_bytes: bytes, received_address: (str, int)):
        super().__init__(message_bytes, received_address)
        names = []
        for i in AudioInputStream.get_devices():
            names.append(i['name'])
        print(names)
        self.response_json = {
            "devices": names,
            "functions": {}
        }

    def get_response(self) -> (bytes, (str, int)):
        try:
            body = json.dumps(self.response_json)
            resp_bytes = struct.pack("!hhI{}s".format(len(body)),
                                     self.opcode,
                                     self.message_len,
                                     self.message_id,
                                     bytes(body,'utf-8'))
            return resp_bytes, self.received_address
        except Exception as e:
            print(e)
            return bytes("", 'utf-8')

InfoMessage(b'000000000000000000000000000', ('',9))

