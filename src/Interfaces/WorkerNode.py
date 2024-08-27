import logging
import os
import signal
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from threading import Thread
from typing import List
from kademlia_network.kademlia_heap_node import KademliaHeapNode
from src.kademlia_network.kademlia_node_data import KademliaNodeData

log = logging.getLogger(__name__)


class Worker_Node(KademliaHeapNode):
    def __init__(self, host, port):
        super().__init__(host=host, port=port)
        self.configure_worker_endpoints()

    def configure_worker_endpoints(self):
        @self.app.route("/global/ping", methods=["GET"])
        def global_ping():
            response = self.global_ping()
            return jsonify(response), 200

        @self.app.route("/leader/update_admins_entry_points")
        def update_admins_entry_points_as_leader():
            data = request.get_json(force=True)
            register_idx = data.get("register_idx")
            entry_points = [
                KademliaNodeData.from_json(node) for node in data.get("entry points")
            ]
            response = self.update_admins_entry_points_as_leader(
                entry_points, register_idx
            )
            return jsonify(response), 200

    def global_ping(self):
        return {"status": "OK"}

    def update_admins_entry_points_as_leader(
        self, entry_points: List[KademliaNodeData], register_idx: int
    ):
        idx = self.get_length("entry points") - 1
        while idx > register_idx:
            node = self.list_get(idx)
            address = f"{node.ip}:{node.port}"
            response = self.call_rpc(address, "global_ping", {})
            if response and response.get("status") == "OK":
                break
            self.pop_as_leader("entry points")
            idx -= 1
        for entry_point in entry_points:
            self.push("entry points", entry_point.to_json())
        return {"status": "OK"}

    def register(self, entry_points: List[KademliaNodeData]):
        """Este metodo une el worker a la red. Toma como parametro la direccion de otros nodos worker que
        usara para el bootstrapping. Una vez en la red podra conocer a que entry_points de la red de administradores
        puede solicitarle su registro"""
        self.bootstrap(entry_points)
        idx = self.get_length("entry points") - 1
        while idx >= 0:
            entry_point = KademliaNodeData.from_json(self.list_get(idx))
            address = f"{entry_point.ip}:{entry_point.port}"
            data = {"role": "scrapper", "node": self.node_data.to_json()}
            response = self.call_rpc(address, "follower/register", data)
            if response and response.get("status") == "OK":
                address = self.find_leader_address()
                data = {
                    "register_idx": idx,
                    "entry points": response.get("entry points"),
                }
                self.call_rpc(address, "leader/update_admins_entry_points", data)
                break
            idx -= 1
        return idx >= 0
