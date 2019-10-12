import socket
import struct
from threading import Thread
import wave
import json
import numpy as np

UDPPORT = 12345
TCPPORT = 44444

TOADDR = "192.168.0.5"

def listen_tcp(sockfd):
    print("Receiving audio")
    wavfile = wave.open("sound.wav", 'w')
    wavfile.setnchannels(2)
    wavfile.setsampwidth(2)
    wavfile.setframerate(44100)
    i=0
    try:
        while True:
            data = sockfd.recv(1024)
            wavfile.writeframes(data)
    except KeyboardInterrupt:
        pass
    wavfile.close()



def write_to_wav(data, open_wavfile):
    open_wavfile.writeframesraw(data)


def print_data(data):
    print(data)



# setup sockets to be used, udp socket on 12345, and tcp socket on 44444
udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udpsock.bind(("", UDPPORT))

tcpserv = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
tcpserv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpserv.bind(("", TCPPORT))
tcpserv.listen()



# write device message to udp
infomessage = struct.pack("!hhI", 1, 0, 1)
udpsock.sendto(infomessage, (TOADDR, 9588))
response_msg, addr = udpsock.recvfrom(1024)
print(str(response_msg[8:], 'utf-8'))
jsondict = json.loads(str(response_msg[8:], 'utf-8'))

wanted_device = jsondict['devices'][0]

tcpStreamRequest = bytes(json.dumps({
    "device": wanted_device,
    "port": TCPPORT,
    "id": 1  # this is currently trivial
}), 'utf-8')

tcpStreamRequestBytes = struct.pack("!hhI{}s".format(len(tcpStreamRequest)),
                                    3,
                                    len(tcpStreamRequest),
                                    1,
                                    tcpStreamRequest)
udpsock.sendto(tcpStreamRequestBytes, (TOADDR, 9588))

while True:
    newsock, addr = tcpserv.accept()
    Thread(target=listen_tcp, args=(newsock,)).start()