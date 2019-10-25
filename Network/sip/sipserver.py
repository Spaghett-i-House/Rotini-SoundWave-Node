import http.server
import socketserver
from threading import Thread
from Network.sip.siprequesthandler import SIPRequestHandler
from Network.sip.sipregistry import SIPRegistry
SIPPORT = 5060


class SIPServer(object):

    def __init__(self, broker_address: (str, int)):
        self.close_flag = False
        # server socket
        #self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.sockfd.connect(broker_address)
        self.handler = SIPRequestHandler
        self.handler.registry = SIPRegistry()
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("", SIPPORT), self.handler)

        # TODO start broadcast of contact information over server
        print("[STATUS]SIP Server listening")
        self.httpd.serve_forever()
        #self.httpd.





SIPServer(("",0))