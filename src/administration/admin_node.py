import logging
import requests
from flask import Flask, request, jsonify
from threading import Thread
from kademlia_network.kademlia_queue_node import KademliaQueueNode
from Interfaces.NodeData import NodeData
from src.Interfaces.IStorage import IStorage
from src.kademlia_network.kademlia_node_data import KademliaNodeData

log = logging.getLogger(__name__)


class Admin_Node(KademliaQueueNode):
    def __init__(
        self,
        node_id=None,
        storage: IStorage = None,
        ip=None,
        port=None,
        ksize: int = 2,
        alpha=3,
        max_chunk_size=2,
    ):
        super().__init__(node_id, storage, ip, port, ksize, alpha)
        self.max_chunk_size = max_chunk_size
        self.configure_admin_endpoints()
        self.is_leader = False

    def configure_admin_endpoints(self):
        @self.app.route("/global_ping", methods=["POST"])
        def global_ping():
            return jsonify({"status": "OK"}), 200

        @self.app.route("/follower/register", methods=["POST"])
        def follower_register():
            data = request.get_json(force=True)
            role, node = data.get("role"), data.get("node")
            node = KademliaNodeData.from_json(node)
            response = self.follower_register(role, node)
            return jsonify(response), 200

        @self.app.route("/leader/register", methods=["POST"])
        def leader_register():
            data = request.get_json(force=True)
            role, node = data.get("role"), data.get("node")
            self.leader_register(role, node)
            return jsonify({"status": "OK"}), 200

        @self.app.route("/leader/run", methods=["POST"])
        def leader_run():
            self.leader_run()
            return jsonify({"status": "OK"}), 200

        @self.app.route("/leader/handle_scrap_result")
        def handle_scrap_result():
            data = request.get_json(force=True)
            urls = data.get("url")
            scrapper = NodeData.from_json(data.get("scrapper"))
            state = data.get("state")
            self.handle_scrap_result(urls, scrapper, state)
            return jsonify({"status": "OK"}), 200

        @self.app.route("/follower/scrap")
        def scrap():
            data = request.get_json(force=True)
            url = data.get("url")
            scrapper = NodeData.from_json(data.get("scrapper"))
            follower_scrap(scrapper, url)

    def follower_register(self, role, node: KademliaNodeData):
        pass

    def leader_register(self, role, node):
        pass

    def leader_run(self):
        pass

    def handle_scrap_results(self, urls, scrapper, state):
        pass

    def follower_scrap(self, scrapper, url):
        pass
