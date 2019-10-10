import soundcard as sc
from Audio.AudioInputStream import AudioInputStream

class SystemAudio(object):

    def __init__(self):
        self.stream_obj_map = {}

    def get_audio_stream(self, device_name: str, id: str) -> AudioInputStream:
        '''
        get_audio_stream gets a stream of audio data
        :param device_name: the string representation of an imput device
        :throws DeviceNotFound
        :return: a deviceInputStream object representing input data
        '''
        mic = sc.get_microphone(device_name, include_loopback=True)
        if mic is not None:
            new_stream = AudioInputStream(mic)
            self.stream_obj_map[id] = new_stream
            return new_stream
        else:
            raise(IOError("Audio device not found"))

    def close_audio_stream(self, identifier: str) -> bool:
        if self.stream_obj_map.get(identifier):
            self.stream_obj_map.get(identifier).close()
            return True
        return False

    @staticmethod
    def get_mic_names() -> [str]:
        idlist = []
        for i in sc.all_microphones(include_loopback=True):
            idlist.append(i.id)
        return idlist
