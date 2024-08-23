import asyncio
import pickle
import threading
import aiohttp
from flask import Flask, jsonify, request
import requests
import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))

from src.Interfaces.IStorage import IStorage
from src.kademlia_network.node_data import NodeData
from src.kademlia_network.routing_table import Routing_Table
from src.kademlia_network.storage import Storage
from src.utils.utils import digest, gather_dict
from sortedcontainers import SortedList
import logging

log = logging.getLogger(__name__)


class Node:
    def __init__(
        self,
        node_id,
        storage: IStorage = None,
        ip=None,
        port=None,
        ksize: int = 2,
        alpha=3,
    ):
        self.storage = storage or Storage()
        self.alpha = alpha
        self.id = node_id
        self.host = ip
        self.port = port
        self.ksize = ksize
        self.router = Routing_Table(self, ksize)
        self.node_data = NodeData(ip=self.host, port=self.port, id=self.id)
        self.app = Flask(__name__)
        self.configure_endpoints()

    def configure_endpoints(self):
        @self.app.route("/ping", methods=["POST"])
        def ping():
            data = request.get_json(force=True)
            node = NodeData.from_json(data.get("sender_node_data"))
            response = self.ping(node)
            return jsonify(response), 200

        @self.app.route("/store", methods=["POST"])
        def store():
            data = request.get_json(force=True)
            node = NodeData.from_json(data.get("sender_node_data"))
            response = self.store(node, data.get("key"), data.get("value"))
            return jsonify(response), 200

        @self.app.route("/find_value", methods=["POST"])
        def find_value():
            data = request.get_json(force=True)
            node = NodeData.from_json(data.get("sender_node_data"))
            response = self.find_value(node, data.get("key"))
            return jsonify(response), 200

        @self.app.route("/find_node", methods=["POST"])
        def find_node():
            data = request.get_json(force=True)
            node = NodeData.from_json(data.get("sender_node_data"))
            response = self.find_node(node, data.get("key"))
            return jsonify(response), 200

    def ping(self, node: NodeData):
        self.welcome_if_new(node)
        return {"status": "OK"}

    def store(self, node: NodeData, key, value):
        self.welcome_if_new(node)
        log.debug(
            "got a store request from node %s, storing '%s'='%s'", node.id, key, value
        )
        self.storage[key] = value
        return {"status": "OK"}

    def find_value(self, node: NodeData, key):
        value = self.storage.get(key)
        if value is None:
            return self.find_node(node, key)
        self.welcome_if_new(node)
        return {"status": "OK", "value": value}

    def find_node(self, node: NodeData, key):
        log.info("finding neighbors of %i in local table", key)
        self.welcome_if_new(node)
        closest_nodes = [node.to_json() for node in self.router.k_closest_to(key)]
        return {"status": "OK", "nodes": closest_nodes}

    async def call_ping(self, node_to_ask: NodeData):
        """Llama a PING en otro nodo"""
        address = f"{node_to_ask.ip}:{node_to_ask.port}"
        response = await self.call_rpc(
            address, "ping", {"sender_node_data": self.node_data.to_json()}
        )
        if response is None:
            print(f"No response from node {node_to_ask.ip}:{node_to_ask.port}")
            return False

        return response.get("status") == "OK"

    async def call_store(self, node_to_ask: NodeData, key, value):
        """Llama a STORE en otro nodo"""
        address = f"{node_to_ask.ip}:{node_to_ask.port}"
        response = await self.call_rpc(
            address,
            "store",
            {"sender_node_data": self.node_data, "key": key, "value": value},
        )
        if response is None:
            print(f"No response from node {node_to_ask.ip}:{node_to_ask.port}")
            return False

        return response.get("status") == "OK"

    async def call_find_value(self, node_to_ask: NodeData, key):
        """Llama a FIND_VALUE en otro nodo"""
        address = f"{node_to_ask.ip}:{node_to_ask.port}"
        response = await self.call_rpc(
            address,
            "find_value",
            {"sender_node_data": self.node_data, "key": key},
        )
        if response is None:
            print(f"No response from node {node_to_ask.ip}:{node_to_ask.port}")
            return False
        return response.get("value") if response.get("value") else response.get("nodes")

    async def call_find_node(self, node_to_ask: NodeData, key):
        """Llama a FIND_NODE en otro nodo"""
        address = f"{node_to_ask.ip}:{node_to_ask.port}"
        response = await self.call_rpc(
            address,
            "find_node",
            {"sender_node_data": self.node_data.to_json(), "key": key},
        )
        if response is None:
            print(f"No response from node {node_to_ask.ip}:{node_to_ask.port}")
            return False
        return [NodeData.from_json(node) for node in response.get("nodes")]

    def listen(self):
        # Correr el servidor Flask en un hilo separado para no bloquear
        def run_app():
            self.app.run(host=self.host, port=self.port, threaded=True)

        thread = threading.Thread(target=run_app)
        thread.start()

    async def call_rpc(self, node_address, endpoint, data):
        url = f"http://{node_address}/{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    response.raise_for_status()
                    return await response.json()
        except asyncio.TimeoutError:
            print(f"Timeout occurred when calling {url}")
            return None
        except aiohttp.ClientConnectorError as e:
            print(f"Connection refused or network error when calling {url}: {e}")
            return None
        except aiohttp.ClientError as e:
            print(f"ClientError occurred when calling {url}: {e}")
            return None

    def welcome_if_new(self, node: NodeData):
        """Añade un nodo a la tabla de enrutamiento si es nuevo"""
        if not node.id in self.router:
            return

        log.info("never seen %s before, adding to router", node)
        for key, value in self.storage:
            keynode_id = digest(key)
            neighbors = self.router.k_closest_to(keynode_id)
            if neighbors:
                last = distance_to(neighbors[-1].id, keynode_id)
                new_node_close = distance_to(node.id, keynode_id) < last
                first = distance_to(neighbors[0].id, keynode_id)
                this_closest = distance_to(self.id, keynode_id) < first
            if not neighbors or (new_node_close and this_closest):
                asyncio.create_task(self.call_store(node, key, value))
        self.router.add(node)

    async def lookup(self, id):
        """Realiza una búsqueda para encontrar los k nodos más cercanos a un ID"""
        log.info(f"Initiating lookup for key {id}")

        # Inicializar el conjunto de nodos más cercanos a partir de la tabla de enrutamiento
        nearest = SortedList(
            [
                (distance_to(id, contact.id), contact)
                for contact in self.router.k_closest_to(id)
            ]
        )
        if not nearest:
            log.warning(f"No known neighbors to lookup key {id}")
            return []

        # Iniciar las consultas a los alpha nodos más cercanos
        already_queried = set()

        while True:
            responses = []
            # Seleccionamos hasta alpha nodos para consultar simultáneamente
            tasks = [
                self.call_find_node(n, id)
                for _, n in nearest
                if not n.id in already_queried
            ]
            nodes_to_query = [n for _, n in nearest if not n.id in already_queried]
            results = await asyncio.gather(*tasks)
            results = zip(results, nodes_to_query)

            for result, n in results:
                if result[0]:
                    responses.extend([NodeData(n.ip, n.port, n.id) for n in result[1]])

            for n in responses:
                if n.id not in already_queried:
                    nearest.add(distance_to(n.id, id), n)
                    already_queried.add(n.id)

            nearest = nearest[: self.ksize]
            if all(x in already_queried for x in nearest):
                break

        return nearest

    def save_state(self, fname):
        """Guarda el estado del nodo en un archivo"""
        log.info(f"Saving state to {fname}")
        data = {
            "ksize": self.ksize,
            "alpha": self.alpha,
            "id": self.id,
            "storage": self.storage,
            "neighbors": self.bootstrappable_k_closest(),
            "router": self.router,
        }
        with open(fname, "wb") as f:
            pickle.dump(data, f)

    @classmethod
    async def load_state(cls, fname, port, interface="0.0.0.0"):
        """Carga el estado del nodo desde un archivo"""
        log.info(f"Loading state from {fname}")
        with open(fname, "rb") as f:
            data = pickle.load(f)

        node = cls(
            node_id=data["id"],
            storage=data["storage"],
            ip=interface,
            port=port,
            ksize=data["ksize"],
            alpha=data["alpha"],
        )
        node.router = data["router"]
        await node.listen(port, interface)
        if data["neighbors"]:
            await node.bootstrap(data["neighbors"])
        return node


def distance_to(node_1_id, node_2_id):
    # Calcula la distancia de un nodo a otro nodo usando XOR
    return node_1_id ^ node_2_id
