from collections import namedtuple
from typing import NamedTuple
import json


# class NodeData(NamedTuple):
#     id: int
#     ip: str = ""
#     port: int = 0
class NodeData:
    def __init__(self, id: int, ip: str = "", port: int = 0):
        self.id = id
        self.ip = ip
        self.port = port

    def to_json(self):
        return json.dumps({"id": self.id, "ip": self.ip, "port": self.port})

    @classmethod
    def from_json(cls, json_str):
        dict = json.loads(json_str)
        return cls(dict["id"], dict["ip"], dict["port"])

    def __str__(self) -> str:
        return f"ID:{self.id} -> ADRESS:{self.ip}:{self.port}"
