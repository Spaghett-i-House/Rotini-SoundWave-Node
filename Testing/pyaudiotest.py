import soundcard as sc
import scipy.io.wavfile
import wave
import socket
import numpy as np

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
socket.setsockopt(socket.SOL_SOCKET, socket.)
socket.bind(("", 9577))

wa = wave.open('wav.wav', 'w')
wa.setsampwidth(4)
wa.setframerate(48000)
wa.setnchannels(1)
default_mic = sc.default_microphone()
socket
with default_mic.recorder(samplerate=48000, channels=1) as mic:
    while True:
        data = mic.record(numframes=1024)
        print(data.dtype)
        print(len(data))
        scipy.io.wavfile.write("asdasdasd.wav", 48000, data)