from Network.rtp.rtpsession import RTPSession
from Network.rtp.rtppacket import RTPPayloadType
import soundcard as sc
import numpy as np
from threading import Thread
import time
import random as rand

class RTPSoundSession(object):

    def __init__(self, data_addr: (str, int), control_addr: (str, int), audio_source: str,
                 ssrc: int, start_sequence, on_end_callback: callable(str)):
        self.close_flag = False
        self.data_addr = data_addr
        self.control_addr = control_addr
        self.audio_source = audio_source
        self.ssrc = ssrc
        self.on_end = on_end_callback
        # TODO: finish implementing session
        self.session = RTPSession(data_addr, control_addr, ssrc, start_sequence, self.on_rtpc_end)
        #TODO: add thread to receive and set up audio
        #TODO: add audio to session
        self.audio_thread = Thread(target=self.audio_reception_thread)
        self.audio_thread.start()

    def audio_reception_thread(self):
        audio_device = sc.get_microphone(self.audio_source, include_loopback=True)
        print("Starting recording on device", audio_device.id)
        with audio_device.recorder(samplerate=44100, channels=1) as mic:
            while not self.close_flag:
                data = mic.record(numframes=1024)
                # data is originally a np.float32 from -1 to 1
                timestamp = time.time()-float(1571300000.0)
                data_as_short = np.short(data*32767).tobytes()
                self.session.add_data_to_stream(data_as_short, 50, RTPPayloadType.SHORT, timestamp) # TODO: cscp should not be 50

    def on_rtpc_end(self):
        self.close_flag = True
        self.audio_thread.join()
        self.on_end(self.ssrc)
