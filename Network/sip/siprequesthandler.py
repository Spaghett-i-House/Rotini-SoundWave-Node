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
from Network.rtp.rtpstream import RTPStream
from Network.sip.sipregistry import SIPRegistry
from Network.customsdp.csdpmessage import CSDPMessage
SIP_VERSION = "2" # I DO not know

class SIPRequestHandler(BaseRequestHandler):
    registry: SIPRegistry

    def handle(self):
        data = self.request.recv(1024).strip()
        print("{} wrote: {}".format(self.client_address[0], data))
        request_data = SIPRequest.from_string(data.decode('utf-8'))
        request_data.print()
        switch = {
            "REGISTER": self.on_register,
            "INVITE": self.on_invite,
            "ACK": self.not_implemented,
            "CANCEL": self.not_implemented,
            "OPTIONS": self.not_implemented
        }
        function = switch.get(request_data.method,
                              lambda: print("[WARNING], No request matches {}".format(request_data.method)))
        f_return = function(request_data)

    def on_register(self, sip_request: SIPRequest):
        headers = sip_request.headers
        to = headers.get('To')

        if to is None:
            failure_response = SIPResponse(SIP_VERSION, SIPCodes.SERVER_INTERNAL_ERROR, "No To Header", {})
            self.request.sendall(failure_response.serialize())
            return
        self.registry.add_address(to)
        ok_response = SIPResponse(SIP_VERSION, SIPCodes.OK, "Success", {})
        self.request.sendall(ok_response.serialize())


    def on_invite(self, sip_request: SIPRequest):
        # look at headers
        # Invite body is an SDP Message describing the RTP request
        session_descriptor = CSDPMessage.from_string(sip_request.body)
        #print(session_descriptor)
        #TODO Create Session of RTP from session descriptor
        print("[STATUS] RTP Created with", sip_request.body)

        # send trying message
        """trying_response = SIPResponse(SIP_VERSION, SIPCodes.TRYING, "asd", {})
        self.request.sendall(trying_response.serialize())
        ringing_response = SIPResponse(SIP_VERSION, SIPCodes.RINGING, "asd", {})
        self.request.sendall(ringing_response.serialize())"""
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
        rtp_session = RTPStream((addr, int(port))) #audio_resource=device_name)
        # await bye
        self.request.settimeout(None)
        while True:
            data = self.request.recv(1024).strip()
            request_data = SIPRequest.from_string(data.decode('utf-8'))
            request_data.print()
            if request_data.method == SIPMethod.BYE:
                rtp_session.close()
                # TODO end rtp
                print("ENDING RTP")
                break

        ok_response = SIPResponse(SIP_VERSION, SIPCodes.OK, "", {})
        self.request.sendall(ok_response.serialize())

    def not_implemented(self, sip_request: SIPRequest):
        unimplemented_error = SIPResponse(SIP_VERSION, SIPCodes.NOT_IMPLEMENTED, "Not Implemented", {})
        self.request.sendall(unimplemented_error.serialize())



