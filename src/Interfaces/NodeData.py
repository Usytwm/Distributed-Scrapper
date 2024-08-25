import json


class NodeData:
    def __init__(self, ip: str = "", port: int = 0, type="admin"):
        self.ip = ip
        self.port = port
        self.type = type

    def to_json(self):
        return json.dumps({"ip": self.ip, "port": self.port, "type": self.type})

    @classmethod
    def from_json(cls, json_str):
        dict = json.loads(json_str)
        return cls(dict["ip"], dict["port"], dict["type"])

    def __str__(self) -> str:
        return f"ADRESS:{self.ip}:{self.port}:{self.type}"

    def __eq__(self, value: "NodeData") -> bool:
        return self.ip == value.ip and self.port == value.port
