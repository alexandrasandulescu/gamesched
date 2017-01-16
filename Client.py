import socket
import pickle

class Client():
    def __init__(self, host, port):
        self.shutdown = False
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET,
                socket.SOCK_STREAM)

    def decode_msg(self, msg):
        return pickle.loads(msg)

    def encode_msg(self, msg):
        return pickle.dumps(msg, -1)

    def start(self):
        self.socket.connect((self.host, self.port))
        while not self.shutdown:
            try:
                msg = self.socket.recv(512)
                print(self.decode_msg(msg))
                s = input("--> Option:")
                self.socket.send(self.encode_msg(s))
            except KeyboardInterrupt:
                print('KeyboardInterrupt: stopping mainloop')
                self.shutdown = True
                continue
            except:
                traceback.print_exc()
                continue
