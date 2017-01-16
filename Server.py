import socket
import threading
import pickle

class Server():
    def __init__(self, port):
        self.shutdown = False
        self.socket = socket.socket(socket.AF_INET,
                socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,
                socket.SO_REUSEADDR, 1)
        self.socket.bind(('', port))
        self.socket.listen(2)

    def debug(self, msg):
        print("[Server] " + msg)

    def decode_msg(self, msg):
        return pickle.loads(msg)

    def encode_msg(self, msg):
        return pickle.dumps(msg, -1)

    def action(self, option):
        self.debug("Action required by client " + option)
        if option == 1: #login
            self.debug("Client login ...")
            #TODO search for client in db and return client  obj
        elif option == 2: #register
            self.debug("Client register ... ")
            #TODO insert client in db and ret client obj
        elif option == 3: #Request game
            self.debug("Client request new game")
            #TODO show all the games option to client and give rights
        elif option == 4: #Play game
            self.debug("Client play game ...")
            #TODO show all client games and add game in scheduler queue

    def handle_client(self, clientsock):
        self.debug( 'New client ' + str(threading.currentThread().getName()) )
        self.debug( 'Connected ' + str(clientsock.getpeername()) )

        # receive data
        sent = clientsock.send(
                self.encode_msg(
                    "Choose action!\n1. Login\n2. Register\n"))
        recv = clientsock.recv(512)
        option = self.decode_msg(recv)
        self.action(option)

        sent = clientsock.send(self.encode_msg(
            "Choose action!\n3. Request game\n4. Play game\n"))
        option = self.decode_msg(recv)
        self.action(option)


    def mainloop(self):
        '''
        handle each client connection in different thread
        '''
        while not self.shutdown:
            try:
                self.debug("Listening...")
                clientsock, clientaddr = self.socket.accept()
                clientsock.settimeout(None)
                t = threading.Thread( target = self.handle_client,
                        args = [ clientsock ] )
                t.start()

            except KeyboardInterrupt:
                print('KeyboardInterrupt: stopping mainloop')
                self.shutdown = True
                continue
            except:
                traceback.print_exc()
                continue

