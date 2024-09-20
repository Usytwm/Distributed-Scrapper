import json
import sys
from pathlib import Path
from typing import Dict

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


from src.utils.utils import generate_id


class KademliaNodeData:
    def __init__(self, id: int = None, ip: str = "", port: int = 0):
        self.id = id if not (id is None) else generate_id(ip, port)
        self.ip = ip
        self.port = port

    def to_json(self):
        return json.dumps({"id": self.id, "ip": self.ip, "port": self.port})

    @classmethod
    def from_json(cls, json_str):
        if isinstance(json_str, Dict):
            dict = json_str
        else:
            # Si es una cadena JSON, la cargamos
            dict = json.loads(json_str)
        return cls(dict["id"], dict["ip"], dict["port"])

    def __str__(self) -> str:
        return f"ID:{self.id} -> ADRESS:{self.ip}:{self.port}"

    def __eq__(self, value: "KademliaNodeData") -> bool:
        return self.id == value.id and self.ip == value.ip and self.port == value.port
