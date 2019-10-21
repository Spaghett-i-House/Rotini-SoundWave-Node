"""
To better understand what is happening here look at RFC 3261 SIP: Session initiation protocol
as well as the WIKIPEDIA entry on SIP

SIPRequestHandler: Parses an SIP request and performs operations expected
SIPRequest: Parses the "start-line" of an sip request, stores each component
"""

from socketserver import BaseRequestHandler
from Network.sip.siprequest import SIPRequest, SIPMethod
from Network.sip.sipresponse import SIPCodes, SIPResponse
from Network.sdp.sdpmessage import SDPMessage

SIP_VERSION = 2 # I DO not know

class SIPRequestHandler(BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024).strip()
        print("{} wrote: {}".format(self.client_address[0], data))
        request_data = SIPRequest.from_string(data.decode('utf-8'))
        request_data.print()
        switch = {
            "INVITE": self.on_invite,
            "ACK": (),
            "CANCEL": (),
            "OPTIONS": ()
        }
        function = switch.get(request_data.method,
                              lambda: print("[WARNING], No request matches {}".format(request_data.method)))
        f_return = function(request_data)

    def on_invite(self, sip_request: SIPRequest):
        # look at headers
        # Invite body is an SDP Message describing the RTP request
        session_descriptor = SDPMessage.from_string(sip_request.body)
        #TODO Create Session of RTP from session descriptor
        print("[STATUS] RTP Created with", sip_request.body)
        # send trying message
        trying_response = SIPResponse(SIP_VERSION, SIPCodes.TRYING, "asd", {})
        self.request.sendall(trying_response.serialize())
        ringing_response = SIPResponse(SIP_VERSION, SIPCodes.RINGING, "asd", {})
        self.request.sendall(ringing_response.serialize())
        ok_response = SIPResponse(SIP_VERSION, SIPCodes.OK, "asd", {})
        self.request.sendall(ok_response.serialize())

        # await ack
        self.request.settimeout(5)
        data = self.request.recv(1024).strip()
        #self.request.settimeout(0)
        request_data = SIPRequest.from_string(data.decode('utf-8'))
        if request_data.method != SIPMethod.ACK:
            print("NO ACK")
            return
        #TODO start session of RTP
        print("Starting RTP")

        # await bye
        data = self.request.recv(1024).strip()
        while True:
            request_data = SIPRequest.from_string(data.decode('utf-8'))
            request_data.print()
            if request_data.method == SIPMethod.BYE:
                # TODO end rtp
                print("ENDING RTP")
                break

        ok_response = SIPResponse(SIP_VERSION, SIPCodes.OK, "", {})
        self.request.sendall(ok_response.serialize())



