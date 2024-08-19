from operator import itemgetter
import heapq
from enum import Enum, auto

from src.kademlia_network.protocol import KademliaService


class Node:
    def __init__(self, node_id, ip=None, port=None):
        # Inicializa un nodo con su ID, IP , puerto y su rol
        self.id = node_id
        self.ip = ip
        self.port = port
        self.long_id = int(node_id.hex(), 16)
        self.protopcol = KademliaService(self)

    def same_home_as(self, node: "Node"):
        # Verifica si este nodo está en la misma dirección IP y puerto que otro nodo y el id
        return self.ip == node.ip and self.port == node.port and self.id == node.id

    def distance_to(self, node: "Node"):
        # Calcula la distancia a otro nodo usando XOR
        return self.long_id ^ node.long_id

    def __iter__(self):
        return iter([self.id, self.ip, self.port])

    def __repr__(self):
        return repr([self.long_id, self.ip, self.port])

    def __str__(self):
        return f"{self.ip}:{self.port} - Role: {self.role.name}"

    def __eq__(self, value: "Node") -> bool:
        return (
            self.ip == value.ip
            and self.port == value.port
            and self.id == value.id
            and self.long_id == value.long_id
        )
