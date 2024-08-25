import os
import signal
import logging
from flask import Flask, request, jsonify
from threading import Thread

log = logging.getLogger(__name__)

class Scrapper_Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
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