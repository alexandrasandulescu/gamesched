import socket
import threading
import pickle
import sqlite3
import traceback
import os
import subprocess

class Server():
    def __init__(self, port):
        self.shutdown = False
        self.socket = socket.socket(socket.AF_INET,
                socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,
                socket.SO_REUSEADDR, 1)
        self.socket.bind(('', port))
        self.socket.listen(2)
        self.max_subscribers = 10

    def debug(self, msg):
        print("[Server] " + msg)

    def decode_msg(self, msg):
        return pickle.loads(msg)

    def encode_msg(self, msg):
        return pickle.dumps(msg, -1)

    def action(self, option, clientsock):
        self.debug("Action required by client " + option)
        try:
            option = int(option)
        except:
            return 0
        if option == 1: #login
            self.debug("Client login ...")
            username = self.send_msg_to_client(clientsock, "\tUsername:")
            login = sqlite3.connect('db/users.db')
            c = login.cursor()
            c.execute('SELECT * FROM users WHERE username=?', (username,))
            if c.fetchone() == None:
                self.send_msg_to_client(clientsock, "Invalid username.", False)
                clientsock.close()
                return -1

            self.send_msg_to_client(clientsock, "Hello '%s'" % username, False)

            #TODO search for client in db and return client  obj
        elif option == 2: #register
            self.debug("Client register ... ")
            username = self.send_msg_to_client(clientsock, "\tUsername:")
            password = self.send_msg_to_client(clientsock, "\tPassword:")
            conn = sqlite3.connect("db/users.db")
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username=?', (username,))
            if c.fetchone() == None: #user not present in the db
                c.execute('INSERT INTO users(username, password) values (?, ?)', (username, password))
                conn.commit()
            else:
                self.send_msg_to_client(clientsock,
                        "Username **%s** already taken. Please choose another" % username,
                        False)
                return -1
            #TODO insert client in db and ret client obj
        elif option == 3: #Request game
            self.debug("Client request new game")
            #TODO show all the games option to client and give rights
            conn = sqlite3.connect("db/games.db")
            c = conn.cursor()
            c.execute('SELECT * from games')
            while True:
                line = c.fetchone()
                if line == None:
                    break
                self.send_msg_to_client(clientsock, line, False)
            game = self.decode_msg(clientsock.recv(512))
            game = self.decode_msg(clientsock.recv(512)) ## HACK
            print("Client chose game %s" % game)
            c.execute('SELECT * from games WHERE gamename=?', (game, ))
            gameentry = c.fetchone()
            if gameentry == None:
                self.send_msg_to_client(clientsock, "Invalid game name", False)
                return -1
            else:
                if gameentry[-1] > self.max_subscribers:
                    self.send_msg_to_client(clientsock, "Subscription limit reached for game %s" % game, False)
                    return -1
                else:
                    c.execute('UPDATE games SET subscriptions=? where gamename=?', (gameentry[-1] + 1, game))
                    conn.commit()

        elif option == 4: #Play game
            self.debug("Client play game ...")
            #TODO show all client games and add game in scheduler queue
            conn = sqlite3.connect("db/games.db")
            c = conn.cursor()
            gamename = self.send_msg_to_client(clientsock, "Please enter gamename")
            c.execute('SELECT * from games where gamename=?', (gamename, ))
            gameentry = c.fetchone()
            if gameentry == None:
                self.send_msg_to_client(clientsock, "Invalid gamename", False)
                return -1
            path = gameentry[2]
            if not os.path.isfile(path):
                self.send_msg_to_client(clientsock, "Invalid game path %s" % path)
                return -1

            out = subprocess.check_output(path.split())
            self.send_msg_to_client(clientsock, "Game output is %s " % out, False)

        elif option == 5: #Quit
            return -1
        return 0

    def send_msg_to_client(self, clientsock, msg, recv=True):
        sent = clientsock.send(self.encode_msg(msg))
        if not recv:
            return 0

        recv_msg = clientsock.recv(512)
        return self.decode_msg(recv_msg)

    def handle_client(self, clientsock):
        self.debug( 'New client ' + str(threading.currentThread().getName()) )
        self.debug( 'Connected ' + str(clientsock.getpeername()) )

        while True:
            option = self.send_msg_to_client(clientsock, "Choose action!\n1. Login\n2. Register\n3. Request game\n4. Play game\n5. Quit\n")
            ret = self.action(option, clientsock)
            if ret < 0:
                break

        return 0

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

