import socket
import soundcard as sc
import time
import numpy as np
from queue import Queue, Full, Empty
from threading import Thread
from Network.rtp.rtppacket import RTPPacket, RTPPayloadType, decode_rtp


class RTPStream(object):

    def __init__(self, remote_endpoint: (str, int), audio_resource: str = "", ssrc=0):
        # set control variables
        self.close_flag = False
        self.sequence_number = 0
        self.ssrc = ssrc
        # create socket for transfers
        self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockfd.bind(("", 0))
        # create audio device binding
        audio_device = sc.get_microphone(audio_resource, include_loopback=True)
        self.audio_stream = audio_device.recorder(samplerate=44100, channels=1, blocksize=1024)
        # create variables to be externally accessed
        self.address = self.sockfd.getsockname()
        self.endpoint = remote_endpoint
        # create queues for multithreading
        self.audio_out_queue = Queue(maxsize=5)  # setting maxsize allows us to skip bytes if we are too slow
        self.audio_in_queue = Queue(maxsize=5)
        # start threads for output
        self.audio_output_thread = Thread(target=self.get_audio_thread)
        self.network_output_thread = Thread(target=self.send_audio_thread)
        self.audio_output_thread.start()
        self.network_output_thread.start()

        # start threads for input (rtp is bidirectional)
        self.audio_input_queue = Thread(target=self.read_incoming_packets_thread)
        self.audio_input_queue.start()

        # TODO Class for rtp statistics
        # TODO change the input/output structure to take from input/output class rather than sounddevice directly

    def read_incoming_packets_thread(self):
        while not self.close_flag:
            in_packet = self.sockfd.recvfrom()
            in_as_rtp = decode_rtp(in_packet)
            if in_as_rtp.payload_type == RTPPayloadType.SHORT:
                data = np.frombuffer(in_as_rtp.data_bytes, dtype=np.short)
            else:
                data = np.frombuffer(in_as_rtp.data_bytes, dtype=np.int)
            try:
                self.audio_in_queue.put(data)
            except Full:
                continue

    def get_audio_thread(self):
        while not self.close_flag:
            # create timestamp for audio
            timestamp = time.time() - float(1571300000.0)  # make the timestamp convertable to a float32
            # get bytes from audio device
            audio = self.audio_stream.record(numframes=1024)
            # audio is recorded as a np.float32 from -1 to 1, we want this to be a short
            audio_as_short = np.short(audio*32767)
            try:
                self.audio_out_queue.put((audio_as_short, timestamp))
            except Full as e:
                print("[WARNING] Audio queue overflow")
                continue

    def send_audio_thread(self):
        while not self.close_flag:
            try:
                # get data to send
                (audio_as_short, timestamp) = self.audio_out_queue.get(timeout=1)
                audio_short_as_bytes = audio_as_short.tobytes()
                # TODO csrc and ssrc need to be actual things
                # create rtp packet
                rtp_packet = RTPPacket(payload_type=RTPPayloadType.SHORT, sequence_number=self.sequence_number,
                                       timestamp=timestamp, ssrc=self.ssrc, csrc_list=[])
                rtp_packet.set_data_bytes(audio_short_as_bytes)
                # send packet
                self.sockfd.sendto(rtp_packet.serialize(), self.endpoint)
                self.sequence_number += 1
            except Empty:
                # handle queue timeout
                print("[WARNING] No audio is in queue to be sent")
                continue
            except Exception as err:
                # handle all other exceptions
                print("[ERROR]", err.with_traceback())
                break

    def get_address(self) -> (str, int):
        return self.address

    def close(self):
        self.close_flag = True
        if self.network_output_thread.is_alive():
            self.network_output_thread.join()
        if self.audio_input_thread.is_alive():
            self.audio_input_thread.join()

        self.sockfd.close()
        print("[STATUS] RTP Stream has been closed")

