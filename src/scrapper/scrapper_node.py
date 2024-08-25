import os
import signal
import logging
import requests
from flask import Flask, request, jsonify
from threading import Thread
from Interfaces.NodeData import NodeData
from typing import List

log = logging.getLogger(__name__)

class Scrapper_Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.node_data = NodeData(ip= self.host, port = self.port, type= 'scrapper')
        self.app = Flask(__name__)
        self.configure_endpoints()
    
    def listen(self):
        def run_app():
            self.app.run(host=self.host, port=self.port, threaded=True)

        thread = Thread(target=run_app)
        thread.start()
    
    def stop(self):
        pass

    def register(self, entry_points : List[NodeData]):
        for entry_point in entry_points:
            node_address = str(entry_point.ip) + ':' + str(entry_point.port)
            url = f"http://{node_address}/register"
            data = self.node_data.to_json()
            try:
                response = requests.post(url, json= data)
                response.raise_for_status()
                break
            except:
                continue

    def configure_endpoints(self):
        @self.app.route("/scrap")
        def scrap():
            data = request.get_json(force= True)
            url = data.get("url")
            response = self.scrap(url)
            return jsonify(response), 200
    
    def scrap(self, url : str):
        pass