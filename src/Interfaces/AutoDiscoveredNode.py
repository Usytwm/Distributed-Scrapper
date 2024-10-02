import socket
from threading import Thread


class DiscovererNode:
    def __init__(self, ip, port, role):
        self.ip = ip
        self.port = port
        self.role = role
        self.broadcast_ip = "255.255.255.255"
        self.broadcast_port = 50000
        self.listening_to_broadcast = True
        self.entry_points = None
        self.timeout_for_welcome_answers = 5

    def broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        msg = self.pack()
        sock.sendto(msg, (self.broadcast_ip, self.broadcast_port))
        sock.close()

    def listen_to_broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", self.broadcast_port))
        sock.setblocking(False)
        while self.listening_to_broadcast:
            try:
                data, addr = sock.recvfrom(1024)
                ip, port, role = self.unpack(data)
                thread = Thread(
                    target=self.respond_to_broadcast, args=((ip, port), role)
                )
                thread.start()
            except Exception as e:
                continue

    def respond_to_broadcast(self, addr, role):
        pass

    def welcome(self):
        pass

    def pack(self):
        message = f"{self.ip}|{self.port}|{self.role}"
        return message.encode("utf-8")

    def unpack(self, data):
        decoded_message = data.decode("utf-8")
        ip, port, role = decoded_message.split(
            "|"
        )  # Dividir la cadena en IP, puerto y role
        return ip, int(port), role
