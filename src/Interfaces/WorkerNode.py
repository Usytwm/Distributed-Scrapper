import logging
from threading import Thread
import time
from flask import request, jsonify
from typing import List

from src.kademlia_network.kademlia_heap_node import KademliaHeapNode
from src.kademlia_network.kademlia_node_data import KademliaNodeData
from src.Interfaces.AutoDiscoveredNode import DiscovererNode
from src.utils.utils import NodeType

log = logging.getLogger(__name__)


class Worker_Node(KademliaHeapNode, DiscovererNode):
    def __init__(self, host, port, role, id=None):
        KademliaHeapNode.__init__(self, node_id=id, ip=host, port=port)
        DiscovererNode.__init__(self, ip=host, port=port, role=role)
        self.configure_worker_endpoints()
        self.role = role

    def configure_worker_endpoints(self):
        @self.app.route("/welcome", methods=["POST"])
        def welcome():
            data = request.get_json(force=True)
            entry_points = [
                KademliaNodeData.from_json(node) for node in data.get("entry points")
            ]
            role = data.get("role")
            response = self.welcome(entry_points, role)
            return jsonify(response), 200

        @self.app.route("/global_ping", methods=["POST"])
        def global_ping():
            response = self.global_ping()
            return jsonify(response), 200

        @self.app.route("/leader/update_admins_entry_points", methods=["POST"])
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

    def welcome(self, entry_points: List[KademliaNodeData], role: str):
        v = False
        if role != self.role and role == NodeType.ADMIN.value:
            original_entry_point = entry_points[0]
            self.push("entry points", original_entry_point.to_json())
            self.set(
                f"entry_point_element_{original_entry_point.id}",
                original_entry_point.to_json(),
            )
            v = True

        self.entry_points = entry_points if not v else []

    def start(self):
        self.broadcast()
        while True:
            if self.entry_points is not None:
                self.register(self.entry_points, self.role)
                break

        thread = Thread(target=self.listen_to_broadcast)
        thread.start()

    def respond_to_broadcast(self, addr, role):
        if role == self.role:
            ip, port = addr
            self.call_rpc(
                f"{ip}:{port}",
                "welcome",
                {"entry points": [self.node_data.to_json()], "role": self.role},
            )

    def global_ping(self):
        return {"status": "OK"}

    def update_admins_entry_points_as_leader(
        self, entry_points: List[KademliaNodeData], register_idx: int
    ):
        idx = self.get_length("entry points") - 1
        while idx > register_idx:
            node = self.list_get("entry points", idx)
            address = f"{node.ip}:{node.port}"
            response = self.call_rpc(address, "global_ping", {})
            if response and response.get("status") == "OK":
                break
            self.pop_as_leader("entry points")
            idx -= 1
        for entry_point in entry_points:
            is_present = self.get(f"entry_point_element_{entry_point.id}")
            if not is_present:
                self.push("entry points", entry_point.to_json())
                self.set(f"entry_point_element_{entry_point.id}", entry_point.to_json())
        return {"status": "OK"}

    def register(self, entry_points: List[KademliaNodeData], role: str):
        """Este metodo une el worker a la red. Toma como parametro la direccion de otros nodos worker que
        usara para el bootstrapping. Una vez en la red podra conocer a que entry_points de la red de administradores
        puede solicitarle su registro"""
        self.bootstrap(entry_points)
        idx = self.get_length("entry points") - 1
        log.critical(f"Registering to {idx} entry points")
        while idx >= 0:
            try:
                entry_point = KademliaNodeData.from_json(
                    self.list_get("entry points", idx)
                )
            except Exception as e:
                log.error(f"Error al obtener el entry point: {e}")
                idx -= 1
                continue
            address = f"{entry_point.ip}:{entry_point.port}"
            data = {"role": role, "node": self.node_data.to_json()}
            log.critical(f"Registering to {address}")
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
