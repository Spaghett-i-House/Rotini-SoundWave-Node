from Audio.SystemAudio import SystemAudio
from Network.UDPServer import UDPServer
"""sysa = SystemAudio()
names = sysa.get_mic_name()
asa = SystemAudio().get_audio_stream(names[0], "1")

q = asa.get_audio_queue()
while(True):
    bytesa = q.get()
    print(bytesa)"""

userve = UDPServer(9588)