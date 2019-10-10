from threading import Thread
from queue import Queue
import pyaudio

class AudioInputStream(Thread):

    def __init__(self, mic: str):
        self.p = pyaudio.PyAudio()
        self.device_index_map = self.create_name_index_map()
        self.close_flag = False
        if self.device_index_map.get(mic) is not None:
            self.stream = self.p.open(format=pyaudio.paInt8,
                                      channels=1, rate=44100,
                                      input=True, frames_per_buffer=1024,
                                      input_device_index=self.device_index_map[mic])
            self.audio_bytes_queue = Queue()
            Thread.__init__(self)
            self.start()
        else:
            raise(IOError("Audio device not found"))

    def run(self):
        print("Reading stream")
        while not self.close_flag:
            data = self.stream.read(1024, exception_on_overflow = False)
            self.audio_bytes_queue.put(data)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def close(self):
        self.close_flag = True

    def get_audio_queue(self):
        return self.audio_bytes_queue

    @staticmethod
    def create_name_index_map():
        amap = {}
        for i in AudioInputStream.get_devices():
            amap[i['name']] = i['index']
        print(amap)
        return amap

    @staticmethod
    def get_devices():
        p = pyaudio.PyAudio()
        count = p.get_device_count()
        devices =  []
        for i in range(count):
            device = p.get_device_info_by_index(i)
            print(device)
            if(device['maxInputChannels'] > 0):
                devices.append(device)
        return devices
