import socket
from Network.sip.siprequest import SIPRequest, SIPMethod
from Network.sip.sipresponse import SIPResponse, SIPCodes
from Network.sdp.sdpmessage import SDPMessage
import time
from queue import Queue
from threading import Thread


class Client(object):

    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((ip, port))
        self.recv_queue = Queue()
        Thread(target=self.recv_thread).start()

    def recv_thread(self):
        while True:
            data = self.sock.recv(1024).strip()
            self.recv_queue.put(data)

    def send_invite(self):
        sdp = SDPMessage("v", "o", "s", "t", "m", "c")
        request = SIPRequest(SIPMethod.INVITE, "a", "2", {}, sdp.serialize().decode('utf-8'))
        self.sock.send(request.serialize())
        data = self.recv_queue.get()
        response = SIPResponse.from_string(data.decode('utf-8'))
        response.print()
        if response.status_code != "TRYING":
            print("[ERROR]")
            return
        data = self.recv_queue.get()
        response = SIPResponse.from_string(data.decode('utf-8'))
        response.print()
        if response.status_code != "RINGING":
            print("[ERROR] 2")
        data = self.recv_queue.get()
        response = SIPResponse.from_string(data.decode('utf-8'))
        response.print()
        if response.status_code != "OK":
            print("ERROR 3")

        ack_request = SIPRequest(SIPMethod.ACK, "a", "2", {}, "body")
        self.sock.send(ack_request.serialize())

        time.sleep(10)

        bye_request = SIPRequest(SIPMethod.BYE, "a", "2", {}, "body")
        self.sock.send(bye_request.serialize())

c = Client("localhost", 5060)
time.sleep(1)
print("Sending invite")
c.send_invite()