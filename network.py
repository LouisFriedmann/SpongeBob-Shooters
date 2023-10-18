# network.py is the gateway allowing client to send information to the server

# Imports
import socket
import pickle

BYTES_TO_RECEIVE = 4096*2


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "26.76.124.87"
        self.port = 5050
        self.addr = (self.server, self.port)
        self.entities = self.connect()

    def get_entities(self):
        return self.entities

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(BYTES_TO_RECEIVE))
        except socket.error as e:
            print(e)

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(BYTES_TO_RECEIVE))
        except socket.error as e:
            print(e)

