"""
To better understand what is happening here look at RFC 3261 SIP: Session initiation protocol
as well as the WIKIPEDIA entry on SIP

SIPRequestHandler: Parses an SIP request and performs operations expected
SIPRequest: Parses the "start-line" of an sip request, stores each component
"""

from socketserver import BaseRequestHandler


class SIPRequestHandler(BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} wrote: {}".format(self.client_address[0], self.data))
        (request_data, headers, body) = self.parse_sip_request(self.data.decode('utf-8'))


class SIPRequest(object):
    """
    Request: A data storage object to parse and store data of request line
    """
    def __init__(self, request_line: str):
        # format: Request-Line  =  Method SP Request-URI SP SIP-Version CRLF from rfc 3261 SIP
        components = request_line.split(" ")
        print("Components:", components)
        if len(components) < 3:
            raise(AssertionError("SIP Request should have at least 6 elements"))
        self.method = components[0]
        self.request_uri = components[1]
        self.sip_version = components[2]


def parse_sip_request(request_string: str) -> (SIPRequest, dict, str):
    sections = request_string.split('\r\n')
    start_line = sections[0]
    headers = {}
    index = 1
    for i, line in enumerate(sections[1:]):
        if line == "":
            # found the empty line signaling end of headers
            index += 1
            break
        else:
            if line.find(":") >= 0:
                split_header = line.split(":")
                #print(split_header)
                variable_name = split_header[0]
                variable_val = split_header[1]
                headers[variable_name] = variable_val
        index += 1

    body = "\r\n".join(sections[index:])
    print("START-LINE:", start_line)
    print("HEADERS:", headers)
    print("Body:", body)
    return SIPRequest(start_line), headers, body

