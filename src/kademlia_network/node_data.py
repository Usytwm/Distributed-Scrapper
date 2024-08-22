from collections import namedtuple
from typing import NamedTuple


# class NodeData(NamedTuple):
#     id: int
#     ip: str = ""
#     port: int = 0
class NodeData:
    def __init__(self, id: int, ip: str = "", port: int = 0):
        self.id = id
        self.ip = ip
        self.port = port
