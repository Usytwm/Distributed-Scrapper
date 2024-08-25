import logging
import requests
from flask import Flask, request, jsonify
from threading import Thread
from kademlia_network.kademlia_node import KademliaNode

log = logging.getLogger(__name__)

class Admin_Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.node = KademliaNode(ip= self.host, port= )
        self.app = Flask(__name__)
        self.configure_endpoints()
    
    def listen(self):
        def run_app():
            self.app.run(host=self.host, port=self.port, threaded=True)

        thread = Thread(target=run_app)
        thread.start()
    
    def stop(self):
        pass

    def configure_endpoints(self):
        @self.app.route("/scrap")
        def scrap():
            data = request.get_json(force= True)
            url = data.get("url")
            response = self.scrap(url)
            return jsonify(response), 200
    
    def scrap(self, url : str):
        pass