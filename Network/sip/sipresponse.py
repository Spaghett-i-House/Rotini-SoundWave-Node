from Network.sip.sipmessage import SIPMessage
import enum


class SIPCodes:
    TRYING = "100"
    RINGING = "180"
    CALL_FORWARDING = "181"
    QUEUED = "182"
    SESSION_PROGRESS = "183"
    OK = "200"
    MULTIPLE_CHOICES = "300"
    MOVED_PERMANENTLY = "301"
    MOVED_TEMPORARILY = "302"
    USE_PROXY = "305"
    ALTERNATIVE_SERVICE = "380"
    SERVER_INTERNAL_ERROR = "500"
    NOT_IMPLEMENTED = "501"
    #TODO Add all of them https://tools.ietf.org/html/rfc3261#section-21

    @staticmethod
    def from_string(stat_code):
        for i in SIPCodes.__dict__:
            if SIPCodes.__dict__[i] == stat_code:
                return i
        #print(method)


class SIPResponse(SIPMessage):

    def __init__(self, sip_version: str, status_code: SIPCodes, reason_phrase: str, headers: dict):
        super().__init__(headers)
        self.sip_version = str(sip_version)
        self.status_code = str(status_code)
        self.reason_phrase = reason_phrase

    def serialize(self) -> bytes:
        lines = self.sip_version + " " + self.status_code + " " + self.reason_phrase + "\r\n"
        for i in self.headers:
            lines += i + ":" + self.headers[i] + "\r\n"

        lines += "\r\n"
        return lines.encode('utf-8')

    @staticmethod
    def from_string(message_string: str):
        message = SIPMessage.from_string(message_string)
        components = message.first_line.split(" ")
        print("Components:", components)
        if len(components) < 3:
            raise(AssertionError("SIP Request should have at least 3 elements"))
        sip_version = components[0]
        status_code = components[1]
        reason_phrase = components[2]
        return SIPResponse(sip_version, SIPCodes.from_string(status_code), reason_phrase, message.headers)

    def print(self):
        print("""
        SIP RESPONSE:
        sip_version: {}
        status_code: {}
        reason_phrase: {}
        headers: {}
        """.format(self.sip_version,
                   self.status_code,
                   self.reason_phrase,
                   self.headers))
