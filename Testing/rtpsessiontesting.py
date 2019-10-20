from Network.rtp.rtpsession import RTPSession
from Network.rtp.rtppacket import decode_rtp
from Network.rtp.rtcppacket import decode_rtcp
from Network.rtpsoundsession import RTPSoundSession
import soundcard as sc
import socket
from threading import Thread
import struct
import wave
import numpy as np
import time

DATA_PORT = 9577
CONTROL_PORT = 9578

mywav = wave.open('sounda.wav', 'w')
mywav.setframerate(44100)
mywav.setsampwidth(2)
mywav.setnchannels(1)
output = sc.default_speaker()
player = output.player(samplerate=44100)
# get a list of all speakers:
speakers = sc.all_speakers()
# get the current default speaker on your system:
default_speaker = sc.default_speaker()
# get a list of all microphones:
mics = sc.all_microphones()
# get the current default microphone on your system:
default_mic = sc.default_microphone()

def listen_data_sock(sock: socket.socket):
    with default_speaker.player(samplerate=44100) as sp:
        while True:
            message, sender = sock.recvfrom(15000)
            msg = decode_rtp(message)
            #print(len(message))
            recv_at = time.time() - float(1571300000.0)
            latenct = recv_at-msg.timestamp
            #print("LATENCY:", latenct)
            #msg.print()
            mywav.writeframes(msg.data_bytes)
            arr = np.frombuffer(msg.data_bytes, dtype=np.short)/32767

            #data_f32 = np.float32(/ 32767)
            sp.play(arr)


def listen_control_sock(sock: socket.socket):
    while True:
        message, sender = sock.recvfrom(1024)
        msg = decode_rtcp(message)
        msg.print()
        if msg.packet_type == 4:
            (addr1, p1, addr2, p2) = struct.unpack("!4sI4sI", msg.data)
            addr1 = socket.inet_ntop(socket.AF_INET, addr1)
            addr2 = socket.inet_ntop(socket.AF_INET, addr2)
            print("Received connection from", addr1, p1, addr2, p2)


sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_data.bind(("", DATA_PORT))

sock_control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock_control.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_control.bind(("", CONTROL_PORT))

Thread(target=listen_control_sock, args=(sock_control,)).start()
Thread(target=listen_data_sock, args=(sock_data,)).start()

rtpsesh = RTPSoundSession(("192.168.0.38", DATA_PORT), ("192.168.0.38", CONTROL_PORT), "", 19274, 0, print)

