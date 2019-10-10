from Network.Messages.Message import Message

class MessageWithResponse(Message):

    def __init__(self, message_bytes: bytes, received_address: (str, int)):
        super().__init__(message_bytes, received_address)

    def get_response(self) -> (bytes, (str, int)):
        raise(NotImplementedError("get_response"))