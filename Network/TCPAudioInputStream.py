from Audio.AudioInputStream import AudioInputStream
from threading import Thread
from queue import Empty
import socket

class TCPAudioInputStream(Thread):

    def __init__(self, audio_stream: AudioInputStream, to_addr: (str, int)):
        self.audio_stream = audio_stream.get_audio_queue()
        self.close_f = False
        self.to_addr = to_addr

        self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        Thread.__init__(self)
        self.start()

    def close(self):
        self.audio_stream.close()
        self.close_f = True

    def run(self):
        try:
            self.sockfd.connect(self.to_addr)
            while not self.close_f:
                try:
                    audio_data = self.audio_stream.get(timeout=1)
                    self.sockfd.send(audio_data)
                except Empty:
                    continue
        except Exception as e:
            print(e)
            self.close_f = True