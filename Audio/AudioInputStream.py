import soundcard as sc
from threading import Thread
from queue import Queue
import numpy as np

SAMPLERATE = 44100
CHUNKSIZE = 16

class AudioInputStream(Thread):

    def __init__(self, mic):
        # Thread control
        self.close_flag = False
        # Audio control
        self.mic = mic
        self.audio_bytes_queue = Queue()

        #Thread Init
        Thread.__init__(self)
        self.start()

    def run(self):
        with self.mic.recorder(samplerate=SAMPLERATE) as mic:
            while not self.close_flag:
                data = mic.record(numframes=CHUNKSIZE)
                self.audio_bytes_queue.put(np.short(data*32767))

    def close(self):
        self.close_flag = True

    def get_audio_queue(self):
        return self.audio_bytes_queue
