from flask import request, jsonify
from kademlia_network.kademlia_node import KademliaNode
from typing import List
from Interfaces.NodeData import NodeData

class StorageNode:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.node = KademliaNode(ip= host, port= port)
        self.app = self.node.app
        self.extend_endpoint()
    
    def extend_endpoint(self):
        @self.app.route("/global/ping", methods=["GET"])
        def global_ping():
            response = self.global_ping()
            return jsonify(response), 200
        
        @self.app.route("/set", methods= ["POST"])
        def set():
            data = request.get_json(force= True)
            key, value = data.get("key"), data.get("value")
            response = self.set(key, value)
            return jsonify(response), 200
        
        @self.app.route("/get", methods= ["GET"])
        def get():
            data = request.get_json(force= True)
            key = data.get("key")
            response = self.get(key)
            return jsonify(response), 200
    
    def global_ping(self):
        return {'status' : 'OK'}
    
    def set(self, key, value):
        self.node.set(key, value)
        return {'status' : 'OK'}
    
    def get(self, key):
        value = self.node.get(key)
        if not (value == False):
            return {'status' : 'OK', 'value' : value}
        else:
            return {'status' : 'OK', 'value' : None}