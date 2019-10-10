from Audio.AudioInputStreamPyaudio import AudioInputStream
from threading import Thread
from queue import Empty
import socket
import struct
import wave

class TCPAudioInputStream(Thread):

    def __init__(self, audio_stream: AudioInputStream, to_addr: (str, int)):
        self.audio_stream = audio_stream
        self.audio_stream_queue = audio_stream.get_audio_queue()
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
                    audio_data = self.audio_stream_queue.get(timeout=1)
                    #print(len(audio_data))
                    for i in audio_data:
                        message = struct.pack("!I", i)
                        self.sockfd.send(message)
                except Empty:
                    continue
        except Exception as e:
            print(e)
            self.close_f = True