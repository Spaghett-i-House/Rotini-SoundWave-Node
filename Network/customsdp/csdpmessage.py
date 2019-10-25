import json

class CSDPMessage(object):

    def __init__(self, d_type: str, source: str, from_addr: str, from_port: str, rtp_port: int, rtp_addr:str):
        self.dtype = d_type
        self.source = source
        self.rtp_port = rtp_port
        self.rtp_addr = rtp_addr
        self.from

    def serialize(self):
        to_json = {
            'type': self.dtype,
            "source": self.source,
            "rtp_port": self.rtp_port,
            "rtp_addr": self.rtp_addr,
            'from': self.from_addr,
            "to": self.to_addr
        }
        return json.dumps(to_json)

    @staticmethod
    def from_string(message: str):
        try:
            message_json = json.loads(message)
            return CSDPMessage(message_json['type'], message_json['source'],
                               message_json['from'], message_json['to'],
                               message_json['rtp_port'], message_json['rtp_addr'])
        except Exception as err:
            print(err.with_traceback())
            raise(AssertionError("CSDP Message could not be decoded"))