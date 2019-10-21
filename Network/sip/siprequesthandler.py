"""
To better understand what is happening here look at RFC 3261 SIP: Session initiation protocol
as well as the WIKIPEDIA entry on SIP

SIPRequestHandler: Parses an SIP request and performs operations expected
SIPRequest: Parses the "start-line" of an sip request, stores each component
"""

from socketserver import BaseRequestHandler
from Network.sip.siprequest import SIPRequest
from Network.sip.sipresponse import SIPCodes, SIPResponse

SIP_VERSION = 2 # I DO not know

class SIPRequestHandler(BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024).strip()
        print("{} wrote: {}".format(self.client_address[0], data))
        request_data = SIPRequest(data.decode('utf-8'))
        request_data.print()
        switch = {
            "INVITE": (),
            "ACK": (),
            "CANCEL": (),
            "OPTIONS": ()
        }
        function = switch.get(request_data.method,
                              lambda: print("[WARNING], No request matches {}".format(request_data.method)))
        f_return = function(request_data)

    def on_invite(self, sip_request: SIPRequest):
        #request header should share the ports my RTP is opening on

        # send trying message
        trying_response = SIPResponse(SIP_VERSION, SIPCodes.TRYING, "", {})
        self.request.sendall(trying_response.serialize())
        #TODO: Should ringing contain ports opened for this?
        ringing_response = SIPResponse(SIP_VERSION, SIPCodes.RINGING, "", {})
        self.request.sendall(ringing_response.serialize())
        ok_response = SIPResponse(SIP_VERSION, SIPCodes.OK, "", {})
        self.request.sendall(ok_response.serialize())
        # open_ports



