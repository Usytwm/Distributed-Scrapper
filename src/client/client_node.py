from threading import Thread

import requests
from src.Interfaces.AutoDiscoveredNode import DiscovererNode
from flask import Flask, jsonify, render_template, request

from src.kademlia_network.kademlia_node_data import KademliaNodeData


class ClientNode(DiscovererNode):
    def __init__(self, host, port):
        DiscovererNode.__init__(self, ip=host, port=port, role="client")
        self.app = Flask(__name__)
        self.configure_client_endpoints()
        self.entry_points = None

    def configure_client_endpoints(self):
        @self.app.route("/welcome", methods=["POST"])
        def welcome():
            data = request.get_json(force=True)
            entry_points = [
                KademliaNodeData.from_json(node) for node in data.get("entry points")
            ]
            response = self.welcome(entry_points)
            return jsonify(response), 200

        # Ruta para renderizar la interfaz
        @self.app.route("/")
        def index():
            return render_template("index.html")

        # Ruta para manejar el guardado de URL
        @self.app.route("/push_url", methods=["POST"])
        def push_url_endpoint():
            url = request.json.get("url")
            if url:
                response = self.push_url(url)
                if response:
                    return jsonify(
                        {"status": "success", "message": "URL guardada correctamente."}
                    )
            return jsonify({"status": "error", "message": "No se pudo guardar la URL."})

        # Ruta para manejar la búsqueda de URL
        @self.app.route("/get_url", methods=["POST"])
        def get_url_endpoint():
            url = request.json.get("url")
            if url:
                response = self.get_url(url)
                if response:
                    return jsonify({"status": "success", "data": response})
            return jsonify({"status": "error", "message": "URL no encontrada."})

    def listen(self):
        def run_app():
            self.app.run(host=self.ip, port=self.port, threaded=True, debug=False)

        thread = Thread(target=run_app)
        thread.start()

    def welcome(self, entry_points):
        self.entry_points = entry_points

    def start(self):
        self.broadcast()
        while True:
            if self.entry_points is not None:
                break

    def call_rpc(self, node_address, endpoint, data):
        url = f"http://{node_address}/{endpoint}"
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def push_url(self, url):
        for node in self.entry_points:
            address = f"{node.ip}:{node.port}"
            data = {
                "url": url,
            }
            response = self.call_rpc(address, "push_url", data)
            if response and response.get("status") == "OK":
                return response

    def get_url(self, url):
        for node in self.entry_points:
            address = f"{node.ip}:{node.port}"
            data = {
                "url": url,
            }
            response = self.call_rpc(address, "get_url", data)
            if response and response.get("status") == "OK":
                return response.get("value")
