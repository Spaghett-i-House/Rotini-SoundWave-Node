import socket
from Network.sip.siprequest import SIPRequest, SIPMethod
from Network.sip.sipresponse import SIPResponse, SIPCodes
from Network.sdp.sdpmessage import SDPMessage
from Network.rtp.rtpstream import RTPStream
import time
from queue import Queue
from threading import Thread
import socketserver
import wave
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
            if len(data) == 0:
                print("Connection closed")
                break

            data = data.split("\r\n\r\n".encode('utf-8'))
            for i in data:
                self.recv_queue.put(i)

    def audio_thread(self, audio_queue):
        wave_file = wave.open("Session_test.wav", "w")
        wave_file.setframerate(44100)
        wave_file.setsampwidth(2)
        wave_file.setnchannels(1)
        while True:
            data = audio_queue.get()
            print(len(data))
            wave_file.writeframes(data)

    def send_invite(self):
        rtp_receive = RTPStream(("", 0), is_receiver=True)
        Thread(target=self.audio_thread, args=(rtp_receive.audio_in_queue,)).start()
        (rtp_addr, rtp_port) = rtp_receive.get_address()
        sdp = SDPMessage(v="2.0", o="gfvandehei IN IP4 "+rtp_addr, s="SDP Audio Stream",
                         t=str(time.time())+" 0", m="audio "+str(rtp_port)+" RTP/AVP 0", c="IN IP4 localhost",
                         a="device_name:")

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