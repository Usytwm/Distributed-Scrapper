import logging
import threading
import time
from typing import List
from flask import Flask, request, jsonify
from threading import Thread, Lock
from src.kademlia_network.kademlia_queue_node import KademliaQueueNode
from src.Interfaces.NodeData import NodeData
from src.Interfaces.IStorage import IStorage
from src.Interfaces.AutoDiscoveredNode import DiscovererNode
from src.kademlia_network.kademlia_node_data import KademliaNodeData
from src.utils.utils import NodeType

log = logging.getLogger(__name__)


class Admin_Node(KademliaQueueNode, DiscovererNode):
    def __init__(
        self,
        node_id=None,
        storage: IStorage = None,
        ip=None,
        port=None,
        ksize: int = 20,
        alpha=3,
        max_chunk_size=2,
        max_depth=1,
    ):
        DiscovererNode.__init__(self, ip, port, NodeType.ADMIN.value)
        KademliaQueueNode.__init__(self, node_id, storage, ip, port, ksize, alpha)
        self.max_chunk_size = max_chunk_size
        self.configure_admin_endpoints()
        self.is_leader = False
        self.max_depth = max_depth
        # self.role = NodeType.ADMIN

    def configure_admin_endpoints(self):
        @self.app.route("/welcome", methods=["POST"])
        def welcome():
            data = request.get_json(force=True)
            entry_points = [
                KademliaNodeData.from_json(node) for node in data.get("entry points")
            ]
            response = self.welcome(entry_points)
            return jsonify(response), 200

        @self.app.route("/global_ping", methods=["POST"])
        def global_ping():
            return jsonify({"status": "OK"}), 200

        @self.app.route("/follower/register", methods=["POST"])
        def follower_register():
            data = request.get_json(force=True)
            role, node = data.get("role"), data.get("node")
            node = KademliaNodeData.from_json(node)
            sucess, entry_points = self.follower_register(role, node)
            if sucess is None:
                return jsonify({"status": "ERROR"}), 500
            if sucess == False:
                return jsonify({"status": "ERROR"}), 400
            return (
                jsonify(
                    {
                        "status": "OK",
                        "entry points": [
                            entry_point.to_json() for entry_point in entry_points
                        ],
                    }
                ),
                200,
            )

        @self.app.route("/leader/register", methods=["POST"])
        def leader_register():
            data = request.get_json(force=True)
            role, node = data.get("role"), KademliaNodeData.from_json(data.get("node"))
            self.leader_register(role, node)
            return jsonify({"status": "OK"}), 200

        @self.app.route("/leader/run", methods=["POST"])
        def leader_run():
            self.start_leader()
            return jsonify({"status": "OK"}), 200

        @self.app.route("/leader_address", methods=["POST"])
        def leader_address():
            return jsonify({"status": "OK", "address": self.find_leader_address()})

        @self.app.route("/leader/handle_scrap_result", methods=["POST"])
        def handle_scrap_result():
            data = request.get_json(force=True)
            urls = data.get("url")
            scrapper = data.get("scrapper")
            scrapper = KademliaNodeData.from_json(scrapper)
            state = data.get("state")
            depth = data.get("depth")
            self.handle_scrap_results(urls, scrapper, state, depth)
            return jsonify({"status": "OK"}), 200

        @self.app.route("/follower/scrap", methods=["POST"])
        def follower_scrap():
            data = request.get_json(force=True)
            url, depth = data.get("url"), data.get("depth")
            scrapper = KademliaNodeData.from_json(data.get("scrapper"))
            storage = KademliaNodeData.from_json(data.get("storage"))
            self.follower_scrap(scrapper, url, storage, depth)
            return jsonify({"status": "OK"}), 200

        @self.app.route("/push_url", methods=["POST"])
        def push_url():
            data = request.get_json(force=True)
            url = data.get("url")
            response = self.push_url(url)
            if response is None:
                return jsonify({"status": "ERROR"}), 500
            return jsonify({"status": "OK"}), 200

        @self.app.route("/get_url", methods=["POST"])
        def get_url():
            data = request.get_json(force=True)
            url = data.get("url")
            response = self.get_url(url)
            if response is None:
                return jsonify({"status": "ERROR"}), 500
            return jsonify({"status": "OK", "value": response}), 200

    def welcome(self, entry_points):
        self.entry_points = entry_points
        return {"status": "OK"}

    def start(self):
        self.broadcast()
        start_time = time.time()
        while time.time() - start_time < self.timeout_for_welcome_answers:
            if self.entry_points is not None:
                self.register(self.entry_points, self.role)
                return
        self.start_leader()
        self.register([], NodeType.ADMIN.value)
        thread = Thread(target=self.listen_to_broadcast)
        thread.start()

    def respond_to_broadcast(self, addr, role):
        ip, port = addr
        entry_points = [self.node_data.to_json()]
        target_role = self.role

        if role == "client":
            closest = self.bootstrappable_k_closest()
            self.call_rpc(
                f"{ip}:{port}",
                "welcome",
                {
                    "role": role,
                    "entry points": [entry_point.to_json() for entry_point in closest],
                },
            )
            return
        # Si el rol es diferente, y está vacío, entonces enviar la respuesta
        if self.role != role and self.is_empty(role):
            self.call_rpc(
                f"{ip}:{port}",
                "welcome",
                {"entry points": entry_points, "role": target_role},
            )
        # Si el rol es el mismo admin, enviar la respuesta directamente
        elif self.role == role:
            self.call_rpc(
                f"{ip}:{port}",
                "welcome",
                {"entry points": entry_points, "role": target_role},
            )

    def push_url(self, url):
        return self.push("urls", (url, 0))

    def get_url(self, url):
        length_storage = self.get_length_queue("storage")
        storage, _, _ = self.select("storage", length_storage)
        if storage is None:
            return None
        response = self.call_rpc(f"{storage.ip}:{storage.port}", "get", {"key": url})
        if response and response.get("status") == "OK":
            return response.get("value")

    def start_leader(self):
        # Este nodo se convierte en el líder y comienza el ciclo
        if self.is_leader:
            return
        log.warning(f"Starting leader in {self.host}:{self.port}")
        self.is_leader = True
        leader_thread = threading.Thread(target=self.leader_run)
        leader_thread.start()

    def stop_leader(self):
        # Detiene el ciclo de líder
        log.info(f"Stopping leader in {self.host}:{self.port}")
        self.is_leader = False

    def follower_register(self, role, node: KademliaNodeData):
        address = self.find_leader_address()
        data = {"role": role, "node": node.to_json()}
        response = self.call_rpc(address, "/leader/register", data)
        if response is None:
            log.debug(f"No response from node {address}")
            return None, None
        entry_points = self.bootstrappable_k_closest()
        if response.get("status") == "OK":
            return True, entry_points
        return False, None

    def register(self, entry_points: List[KademliaNodeData], role: str):
        """Este metodo une el worker a la red. Toma como parametro la direccion de otros nodos worker que
        usara para el bootstrapping. Una vez en la red podra conocer a que entry_points de la red de administradores
        puede solicitarle su registro"""
        register = False
        if entry_points:
            for entry_point in entry_points:
                address = f"{entry_point.ip}:{entry_point.port}"
                data = {"role": role, "node": self.node_data.to_json()}
                response = self.call_rpc(address, "follower/register", data)
                if response and response.get("status") == "OK":
                    register = True
                    break
            self.bootstrap(entry_points)
        else:
            register = self.push(role, self.node_data.to_json())

        return register

    def leader_register(self, role, node: KademliaNodeData):
        ok = self.push(role, node.to_json())
        # log.critical(f"Registering {node} as {role} in {self.node_data}")
        if role == NodeType.ADMIN.value and ok and self.id > node.id:
            response = self.call_rpc(f"{node.ip}:{node.port}", "/leader/run", {})
            if response.get("status") == "OK":
                self.stop_leader()

    def leader_run(self):
        proccess_left = 0
        length_scrapper = 0
        length_storage = 0
        length_admin = 0
        length_urls = 0

        def update_lengths():
            nonlocal proccess_left, length_scrapper, length_storage, length_admin, length_urls
            if proccess_left == 0:
                proccess_left = self.get_length_queue("in_process")
            if length_scrapper == 0:
                length_scrapper = self.get_length_queue("scrapper")
            if length_storage == 0:
                length_storage = self.get_length_queue("storage")
            if length_admin == 0:
                length_admin = self.get_length_queue("admin")
            if length_urls == 0:
                length_urls = self.get_length_queue("urls")

        while self.is_leader:
            update_lengths()
            if length_scrapper and length_urls:
                length_admin, length_scrapper, length_storage, length_urls = self.scrap(
                    length_admin, length_scrapper, length_storage, length_urls
                )
                length_urls -= 1
            if proccess_left:
                length_storage = self.update_in_process(length_storage)

    def scrap(self, length_admin, length_scrapper, length_storage, length_urls):
        admin, admin_address, length_admin = self.select("admin", length_admin)
        if admin is None:
            return 0, length_scrapper, length_storage, length_urls
        response = self.pop("urls")
        if response is None:
            return length_admin, length_scrapper, length_storage, 0
        else:
            url, depth = response
        if url is None:
            return length_admin, length_scrapper, length_storage, 0
        scrapper, _, length_scrapper = self.select(
            "scrapper", length_scrapper, reinsert=False
        )
        if scrapper is None:
            return length_admin, 0, length_storage, length_urls
        storage, _, length_storage = self.select("storage", length_storage)
        if storage is None:
            return length_admin, length_scrapper, 0, length_urls
        if all(x is not None for x in [scrapper, storage, admin]):
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
            self.push("in_process", (url, depth, admin.to_json()))
        return length_admin, length_admin, length_storage, length_urls

    def update_in_process(self, length_storage):
        response = self.pop("in_process")
        if response is None:
            return 0
        url, depth, admin = response
        _, storage_address, length_storage = self.select("storage", length_storage)
        data = {"key": url}
        response = self.call_rpc(storage_address, "get", data)
        value = self.call_ping(KademliaNodeData.from_json(admin))
        if response is None or not value:
            self.push("urls", (url, depth))
        elif response.get("value") == None:
            self.push("in_process", (url, depth, admin))
        return length_storage

    def select(self, role, length_role, reinsert=True):
        while length_role:
            response = self.pop(role)
            if response is None:
                return None, None, 0
            node = KademliaNodeData.from_json(response)
            address = f"{node.ip}:{node.port}"
            response = self.call_rpc(address, "global_ping", {})
            if response and response.get("status") == "OK":
                if reinsert:
                    self.push(role, node.to_json())
                return node, address, length_role
            length_role -= 1
        return None, None, length_role

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
        if response is None or response.get("error") is not None:
            log.debug(f"No response from node {scrapper_address}")
            data = {
                "url": [url],
                "scrapper": scrapper.to_json(),
                "state": False,
                "depth": depth,
            }
        else:
            response_storage = self.call_rpc(
                storage_address,
                "set",
                {
                    "key": url,
                    "value": response.get("content"),
                    "redirection": response.get("redirection"),
                },
            )
            if response_storage is None:
                log.debugf(f"No response from node {scrapper_address}")
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
