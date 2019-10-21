from Network.sip.sipmessage import SIPMessage
import enum


class SIPMethod(enum):
    REGISTER = "REGISTER",
    INVITE = "INVITE",
    ACK = "ACK",
    CANCEL = "CANCEL",
    BYE = "BYE",
    OPTIONS = "OPTIONS"


class SIPRequest(SIPMessage):
    """
    Request: A data storage object to parse and store data of request line
    """
    def __init__(self, method: SIPMethod, request_uri: str, sip_version: str, headers: dict):
        # format: Request-Line  =  Method SP Request-URI SP SIP-Version CRLF from rfc 3261 SIP
        super().__init__(headers)
        self.body = ""
        self.method = method
        self.request_uri = request_uri
        self.sip_version = sip_version

    def serialize(self) -> bytes:
        serial = self.method.value + " " + self.request_uri + " " + self.sip_version + "\r\n"
        for i in self.headers.keys():
            serial += i + ":" + self.headers[i] + "\r\n"
        serial += "\r\n"  # there is no body, but it would be added after CLRF here
        return serial.encode('utf-8')

    @staticmethod
    def from_string(message_string: str):
        message = SIPMessage.from_string(message_string)
        components = message.start_line.split(" ")
        print("Components:", components)
        if len(components) < 3:
            raise(AssertionError("SIP Request should have at least 3 elements"))
        method = components[0]
        request_uri = components[1]
        sip_version = components[2]
        return SIPRequest(SIPMethod(method), request_uri, sip_version, message.headers)

    def print(self):
        print("""
        SIP RESPONSE:
        sip_version: {}
        method: {}
        request_uri: {}
        headers: {}
        """.format(self.sip_version,
                   self.method,
                   self.request_uri,
                   self.headers))


