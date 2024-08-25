import json


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

    def __eq__(self, value: "NodeData") -> bool:
        return self.id == value.id and self.ip == value.ip and self.port == value.port
