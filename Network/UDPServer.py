import socket
from Network.Messages.Message import Message
from Network.Messages.InfoMessage import InfoMessage
from Network.Messages.MessageWithResponse import MessageWithResponse
from Network.Messages.StartStreamMessage import StartStreamMessage


class UDPServer(object):

    def __init__(self, port: int):
        # initialize socket
        print("Server initialization started")
        self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.sockfd.bind(("", port))
        self.sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockfd.settimeout(1)
        self.close_f = False
        self.streamMap = {}
        print("Server has been initialized, listening on {}".format(port))
        #listen on socket
        self.listen()

    def listen(self):
        while not self.close_f:
            try:
                datagram, address = self.sockfd.recvfrom(1024)
                send_bytes, address = self.route_message(datagram, address)
                if send_bytes is not None and address is not None:
                    self.sockfd.sendto(send_bytes, address)
                else:
                    print("Non response message")
            except socket.timeout:
                continue
            except Exception as e:
                print(e)

    def route_message(self, msgBytes: bytes, address: (str, int)) -> (bytes, (str, int)):
        msg = Message(msgBytes, address)
        opcode = msg.get_opcode()
        if opcode == 1:
            # Get info request
            msg = InfoMessage(msgBytes, address)
        elif opcode == 2:
            # ping
            return
        elif opcode == 3:
            # start stream
            msg = StartStreamMessage(msgBytes, address)
            self.streamMap[msg.stream_id] = msg.get_stream()
        elif opcode == 4:
            # stop_stream
            return
        else:
            print("Unknown message type")
        print(type(msg))
        if issubclass(type(msg),MessageWithResponse):
            return msg.get_response()
        else:
            return None, None
