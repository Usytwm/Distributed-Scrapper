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
            role, node = data.get("role"), KademliaNodeData.from_json(data.get("node"))
            self.leader_register(role, node)
            return jsonify({"status": "OK"}), 200

        @self.app.route("/leader/run", methods=["POST"])
        def leader_run():
            self.leader_run()
            return jsonify({"status": "OK"}), 200

        @self.app.route("/leader/stop", methods=["POST"])
        def leader_stop():
            self.is_leader = False
            return jsonify({"status": "OK"}), 200

        @self.app.route("/leader_address", methods=["POST"])
        def leader_address():
            return jsonify({"status": "OK", "address": self.find_leader_address()})

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
            self.follower_scrap(scrapper, url)

    def follower_register(self, role, node: KademliaNodeData):
        address = self.find_leader_address()
        data = {"role": role, "node": node.to_json()}
        response = self.call_rpc(address, "/leader/register", data)
        if response is None:
            log.info(f"No response from node {address}")
            return None
        return response.get("status") == "OK"

    def leader_register(self, role, node: KademliaNodeData):
        self.push(role, node.to_json())

    def leader_run(self):
        while self.is_leader:
            if not self.is_empty("scrapper") and not self.is_empty("urls"):
                admin = KademliaNodeData.from_json(self.pop("admin"))
                self.push("admin", admin.to_json())
                address = f"{admin.ip}:{admin.port}"
                url = self.pop("urls")
                scrapper = self.pop("scrapper")
                data = {"url": url, "scrapper": scrapper}
                thread = Thread(
                    target=self.call_rpc, args=(address, "follower/scrap", data)
                )
                thread.start()
                self.push("in_process", (url, admin.to_json()))
            if not self.is_empty("in_process"):
                url, scrapper = self.pop("in_process")
                address = self.select_storage_address()  #! Implementar
                response = self.call_rpc(address, "get", url)
                if response.get("value") == None and not self.call_ping(admin):
                    self.push("urls", url)
                else:
                    self.push("in_process", (url, scrapper))

    def handle_scrap_results(self, urls, scrapper, state):
        pass

    def follower_scrap(self, scrapper, url):
        pass

    def select_storage_address(self):
        pass
