import socket
from threading import Thread
import struct
import json
import wave
import pyaudio

SERVERUDPPORT = 9599
SERVERUDPADDRESS = "localhost"

def receive_audio(tcpSocket, audioFile):
    tcpSocket.listen(1)
    datasock, addr = tcpSocket.accept()
    try:
        while(True):
            data = datasock.recv(1024)
            print(max(data))
            audioFile.writeframes(data)
            '''for i in data:
                nd = struct.pack("<h", i)
                audioFile.writeframes(nd)'''
            #print(len(data))
            if len(data) == 0:
                break
    except KeyboardInterrupt:
        audioFile.close()

def recieve_udp(udpsock):
    while True:
        data, connection = udpsock.recvfrom(1024)
        print("Received",data,"from",connection)


tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind(('', 44444))

udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udpsock.bind((SERVERUDPADDRESS, SERVERUDPPORT))

p = pyaudio.PyAudio()
wavfile = wave.open("sound.wav", 'wb')
wavfile.setnchannels(1)
wavfile.setsampwidth(p.get_sample_size(pyaudio.paInt8))
wavfile.setframerate(44100)

Thread(target=receive_audio, args=(tcpsock, wavfile, )).start()
Thread(target=recieve_udp, args=(udpsock,)).start()

msgdict = json.dumps({"port": 44444,
                      "device": "Loopback: PCM (hw:2,0)",
                      "id": "1"})
message = struct.pack("!hhI{}s".format(len(bytes(msgdict, 'utf-8'))),
                      3, len(bytes(msgdict, 'utf-8')), 4, bytes(msgdict, 'utf-8'))

udpsock.sendto(message, ("localhost", 9588))



