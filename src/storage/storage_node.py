import requests
from flask import request, jsonify
from kademlia_network.kademlia_node import KademliaNode
from typing import List
from Interfaces.NodeData import NodeData


class StorageNode:
    def __init__(self, host, port):
        self.node_data = NodeData(ip=host, port=port, type="storage")
        self.node = KademliaNode(ip=host, port=port)
        self.app = self.node.app
        self.extend_endpoint()

    def listen(self):
        self.node.listen()

    def stop(self):
        self.node.stop()

    def register(self, entry_points: List[NodeData]):
        for entry_point in entry_points:
            node_address = str(entry_point.ip) + ":" + str(entry_point.port)
            url = f"http://{node_address}/register"
            data = {"node": self.node_data.to_json()}
            try:
                response = requests.post(url, json=data)
                response.raise_for_status()
                break
            except:
                continue

    def extend_endpoint(self):
        @self.app.route("/global/ping", methods=["GET"])
        def global_ping():
            response = self.global_ping()
            return jsonify(response), 200

        @self.app.route("/set", methods=["POST"])
        def set():
            data = request.get_json(force=True)
            key, value = data.get("key"), data.get("value")
            response = self.set(key, value)
            return jsonify(response), 200

        @self.app.route("/get", methods=["GET"])
        def get():
            data = request.get_json(force=True)
            key = data.get("key")
            response = self.get(key)
            return jsonify(response), 200

    def global_ping(self):
        return {"status": "OK"}

    def set(self, key, value):
        self.node.set(key, value)
        return {"status": "OK"}

    def get(self, key):
        value = self.node.get(key)
        if not (value == False):
            return {"status": "OK", "value": value}
        else:
            return {"status": "OK", "value": None}
