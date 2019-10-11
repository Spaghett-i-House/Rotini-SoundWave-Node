from Network.Messages.MessageWithResponse import MessageWithResponse
from Network.TCPAudioInputStream import TCPAudioInputStream
from Network.Messages.Message import Message
from Audio.AudioInputStreamPyaudio import AudioInputStream
import json
import struct
from Network.Messages.MessageWithResponse import MessageWithResponse


class StartStreamMessage(Message):

    def __init__(self, message_bytes: bytes, received_address: (str, int)):
        super().__init__(message_bytes, received_address)
        json_req = json.loads(str(self.body, 'utf-8'))
        self.requested_port = int(json_req['port'])
        self.requested_device = json_req['device']
        self.stream_id = json_req['id']

    def get_stream(self):
        astream = AudioInputStream(self.requested_device)
        return TCPAudioInputStream(astream, (self.received_address[0], self.requested_port))

    def get_response(self) -> (bytes, (str, int)):
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
            return bytes("", 'utf-8')

