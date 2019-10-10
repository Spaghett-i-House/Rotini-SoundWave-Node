from Network.Messages.MessageWithResponse import MessageWithResponse
from Network.Messages.Message import Message
from Audio.SystemAudio import SystemAudio
import json
import struct


class InfoMessage(MessageWithResponse):

    def __init__(self, message_bytes: bytes, received_address: (str, int)):
        super().__init__(message_bytes, received_address)
        audio_device_names = SystemAudio.get_mic_names()
        self.response_json = {
            "devices": audio_device_names,
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


