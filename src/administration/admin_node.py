import logging
from typing import List
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
            depth = data.get("depth")
            self.handle_scrap_results(urls, scrapper, state, depth)
            return jsonify({"status": "OK"}), 200

        @self.app.route("/follower/scrap")
        def follower_scrap():
            data = request.get_json(force=True)
            url, depth = data.get("url"), data.get("depth")
            scrapper = KademliaNodeData.from_json(data.get("scrapper"))
            storage = KademliaNodeData.from_json(data.get("storage"))
            self.follower_scrap(scrapper, url, storage, depth)

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
            self.scrap_if_able()
            self.update_in_process()

    def handle_scrap_results(
        self, urls: List[str], scrapper: KademliaNodeData, state: bool, depth: int
    ):
        if depth < self.max_depth:
            for url in urls:
                self.push("urls", (url, depth + int(state == True)))
        if state:
            self.push("scrapper", scrapper.to_json())

    def follower_scrap(
        self, scrapper: KademliaNodeData, url, storage: KademliaNodeData, depth
    ):
        scrapper_address = f"{scrapper.ip}:{scrapper.port}"
        storage_address = f"{storage.ip}:{storage.port}"
        response = self.call_rpc(scrapper_address, "scrap", {"url": url})
        if response is None:
            log.info(f"No response from node {scrapper_address}")
            data = {
                "url": [url],
                "scrapper": scrapper.to_json(),
                "state": False,
                "depth": depth,
            }
        else:
            response = self.call_rpc(
                storage_address, "set", {"key": url, "value": response.get("content")}
            )
            if response is None:
                log.info(f"No response from node {scrapper_address}")
                data = {
                    "url": [url],
                    "scrapper": scrapper.to_json(),
                    "state": False,
                    "depth": depth,
                }
            else:
                data = {
                    "url": response.get("links"),
                    "scrapper": scrapper.to_json(),
                    "state": True,
                    "depth": depth,
                }
        self.call_rpc(self.find_leader_address(), "leader/handle_scrap_result", data)

    def scrap_if_able(self):
        if not self.is_empty("scrapper") and not self.is_empty("urls"):
            admin, admin_address = self.select("admin")
            url, depth = self.pop("urls")
            scrapper, _ = self.select("scrapper", reinsert=False)
            storage, _ = self.select("storage")
            if (scrapper != None) and (storage != None):
                data = {
                    "url": url,
                    "scrapper": scrapper.to_json(),
                    "storage": storage.to_json(),
                    "depth": depth,
                }
                thread = Thread(
                    target=self.call_rpc, args=(admin_address, "follower/scrap", data)
                )
                thread.start()
                self.push("in_process", (url, admin.to_json()))

    def update_in_process(self):
        if not self.is_empty("in_process"):
            url, admin = self.pop("in_process")
            _, storage_address = self.select("storage")
            response = self.call_rpc(storage_address, "get", url)
            if response.get("value") == None and not self.call_ping(
                KademliaNodeData.from_json(admin)
            ):
                self.push("urls", url)
            else:
                self.push("in_process", (url, admin))

    def select(self, role, reinsert=True):
        while not self.is_empty(role):
            node = KademliaNodeData.from_json(self.pop(role))
            address = f"{node.ip}:{node.port}"
            response = self.call_rpc(address, "global_ping", {})
            if response and response.get("status") == "OK":
                if reinsert:
                    self.push(role, node.to_json())
                return node, address
        return None, None
