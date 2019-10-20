from Network.Messages.MessageWithResponse import MessageWithResponse
from Network.TCPAudioInputStream import TCPAudioInputStream
from Network.Messages.Message import Message
from Audio.SystemAudio import SystemAudio
import json
import struct
from Network.Messages.MessageWithResponse import MessageWithResponse


class StartStreamMessage(MessageWithResponse):

    def __init__(self, message_bytes: bytes, received_address: (str, int)):
        super().__init__(message_bytes, received_address)
        json_req = json.loads(self.body)
        self.data_port = json_req['data_port']
        self.command_port = json_req['command_port']
        self.stream_id = json_req['sdrc']
        self.audio_device = json_req['source']
        self.start_sequence = json_req['start_seq']

    def get_data_tuple(self) -> ((str, int), (str, int), int):
        return ((self.received_address[0], self.data_port),
                (self.received_address[0], self.command_port),
                self.stream_id)

    """def get_response(self) -> (bytes, (str, int)):
        try:
            body = json.dumps({})
            resp_bytes = struct.pack("!hhI{}s".format(len(body)),
                                     self.opcode,
                                     self.message_len,
                                     self.message_id,
                                     bytes(body,'utf-8'))
            return resp_bytes, self.received_address
        except Exception as e:
            print(e)
            return bytes("", 'utf-8')"""

