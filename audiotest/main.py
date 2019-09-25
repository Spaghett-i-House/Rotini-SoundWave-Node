"""Prints audio bytes to the terminal while piping between input and output"""

import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

p = pyaudio.PyAudio()
p2 = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

stream2 = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)
print("* recording")

frames = []

while True:
    try:
        data = stream.read(CHUNK)
        print(data)
        stream2.write(data)
    except KeyboardInterrupt:
        break

stream.stop_stream()
stream.close()
p.terminate()
