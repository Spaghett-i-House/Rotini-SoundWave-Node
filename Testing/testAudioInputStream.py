"""
This file successfully reads system audio, turns out problem was np float32 needed to become short
"""

from Audio.SystemAudio import SystemAudio
import wave
from scipy.io.wavfile import *
import numpy as np
import struct


sysa = SystemAudio()

names = sysa.get_mic_names()
print(names)
stream = sysa.get_audio_stream(names[0], 1024)
audio_queue = stream.get_audio_queue()

wav_output = wave.open('sound.wav', 'wb')
wav_output.setnchannels(2)
wav_output.setsampwidth(2)
wav_output.setframerate(44100)

audiodata = []
for i in range(20000):
    print(i)
    data = audio_queue.get()
    """for i in data:
        data_w = np.short(i*32767)
        print(data_w)
        wav_output.writeframesraw(data_w)"""
    wav_output.writeframesraw(data)

wav_output.close()
stream.close()
