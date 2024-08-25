import json

class NodeData:
    def __init__(self, ip: str = "", port: int = 0):
        self.ip = ip
        self.port = port

    def to_json(self):
        return json.dumps({"ip": self.ip, "port": self.port})

    @classmethod
    def from_json(cls, json_str):
        dict = json.loads(json_str)
        return cls(dict["ip"], dict["port"])

    def __str__(self) -> str:
        return f"ADRESS:{self.ip}:{self.port}"

    def __eq__(self, value: "NodeData") -> bool:
        return self.ip == value.ip and self.port == value.port