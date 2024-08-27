import os
import pickle
import random
import signal
from threading import Thread
from flask import Flask, jsonify, request
import requests
import sys
from pathlib import Path
import logging
from typing import List

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))

from src.Interfaces.IStorage import IStorage
from src.kademlia_network.kademlia_node_data import KademliaNodeData
from src.kademlia_network.routing_table import Routing_Table
from src.kademlia_network.storage import Storage
from src.utils.utils import N_OF_BITS, digest_to_int
from sortedcontainers import SortedList


log = logging.getLogger(__name__)


class KademliaNode:
    def __init__(
        self,
        node_id=None,
        storage: IStorage = None,
        ip=None,
        port=None,
        ksize: int = 2,
        alpha=3,
    ):
        self.storage = storage or Storage()
        self.alpha = alpha
        self.id = (
            node_id
            if not (node_id is None)
            else random.randint(0, (1 << N_OF_BITS) - 1)
        )
        self.host = ip
        self.port = port
        self.ksize = ksize
        self.router = Routing_Table(self, ksize)
        self.node_data = KademliaNodeData(ip=self.host, port=self.port, id=self.id)
        self.app = Flask(__name__)
        self.configure_kademlia_endpoints()

    def listen(self):
        def run_app():
            self.app.run(host=self.host, port=self.port, threaded=True)

        thread = Thread(target=run_app)
        thread.start()

    def stop(self, save_file="data\\node_state.pkl"):
        """Detiene el servidor y guarda el estado"""
        log.info("Deteniendo el servidor y guardando el estado...")
        self.save_state(save_file)
        # Enviar señal para detener el servidor Flask
        os.kill(os.getpid(), signal.SIGINT)

    def configure_kademlia_endpoints(self):
        @self.app.route("/ping", methods=["POST"])
        def ping():
            data = request.get_json(force=True)
            node = KademliaNodeData.from_json(data.get("sender_node_data"))
            response = self.ping(node)
            return jsonify(response), 200

        @self.app.route("/store", methods=["POST"])
        def store():
            data = request.get_json(force=True)
            node = KademliaNodeData.from_json(data.get("sender_node_data"))
            response = self.store(node, data.get("key"), data.get("value"))
            return jsonify(response), 200

        @self.app.route("/find_value", methods=["POST"])
        def find_value():
            data = request.get_json(force=True)
            node = KademliaNodeData.from_json(data.get("sender_node_data"))
            response = self.find_value(node, data.get("key"))
            return jsonify(response), 200

        @self.app.route("/find_node", methods=["POST"])
        def find_node():
            data = request.get_json(force=True)
            node = KademliaNodeData.from_json(data.get("sender_node_data"))
            response = self.find_node(node, data.get("key"))
            return jsonify(response), 200

    def ping(self, node: KademliaNodeData):
        self.welcome_if_new(node)
        return {"status": "OK"}

    def store(self, node: KademliaNodeData, key, value):
        self.welcome_if_new(node)
        log.debug(
            "got a store request from node %s, storing '%s'='%s'", node.id, key, value
        )
        self.storage[key] = value
        return {"status": "OK"}

    def find_value(self, node: KademliaNodeData, key):
        value = self.storage.get(key)
        if value is None:
            node = self.find_node(node, key)
            return node
        self.welcome_if_new(node)
        return {"status": "OK", "value": value}

    def find_node(self, node: KademliaNodeData, key):
        log.info("finding neighbors of %i in local table", key)
        self.welcome_if_new(node)
        closest_nodes = [node.to_json() for node in self.router.k_closest_to(key)]
        return {"status": "OK", "nodes": closest_nodes}

    def call_ping(self, node_to_ask: KademliaNodeData):
        """Llama a PING en otro nodo"""
        address = f"{node_to_ask.ip}:{node_to_ask.port}"
        response = self.call_rpc(
            address, "ping", {"sender_node_data": self.node_data.to_json()}
        )
        if response is None:
            print(f"No response from node {node_to_ask.ip}:{node_to_ask.port}")
            return False

        return response.get("status") == "OK"

    def call_store(self, node_to_ask: KademliaNodeData, key, value):
        """Llama a STORE en otro nodo"""
        address = f"{node_to_ask.ip}:{node_to_ask.port}"
        response = self.call_rpc(
            address,
            "store",
            {"sender_node_data": self.node_data.to_json(), "key": key, "value": value},
        )
        if response is None:
            print(f"No response from node {node_to_ask.ip}:{node_to_ask.port}")
            return False

        return response.get("status") == "OK"

    def call_find_value(self, node_to_ask: KademliaNodeData, key):
        """Llama a FIND_VALUE en otro nodo"""
        address = f"{node_to_ask.ip}:{node_to_ask.port}"
        response = self.call_rpc(
            address,
            "find_value",
            {"sender_node_data": self.node_data.to_json(), "key": key},
        )
        if response is None:
            print(f"No response from node {node_to_ask.ip}:{node_to_ask.port}")
            return False
        return (
            (response.get("value"), True)
            if response.get("value")
            else (response.get("nodes"), False)
        )

    def call_find_node(self, node_to_ask: KademliaNodeData, key):
        """Llama a FIND_NODE en otro nodo"""
        address = f"{node_to_ask.ip}:{node_to_ask.port}"
        response = self.call_rpc(
            address,
            "find_node",
            {"sender_node_data": self.node_data.to_json(), "key": key},
        )
        if response is None:
            print(f"No response from node {node_to_ask.ip}:{node_to_ask.port}")
            return False
        return [KademliaNodeData.from_json(node) for node in response.get("nodes")]

    def call_rpc(self, node_address, endpoint, data):
        url = f"http://{node_address}/{endpoint}"
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            print(f"Timeout occurred when calling {url}")
            return None
        except requests.ConnectionError as e:
            print(f"Connection refused or network error when calling {url}: {e}")
            return None
        except requests.RequestException as e:
            print(f"RequestException occurred when calling {url}: {e}")
            return None

    def welcome_if_new(self, node: KademliaNodeData):
        """Añade un nodo a la tabla de enrutamiento si es nuevo"""
        if node.id in self.router or node.id == self.id:
            return

        log.info("never seen %s before, adding to router", node)
        for key, value in self.storage:
            # keynode_id = digest_to_int(key)
            neighbors = self.router.k_closest_to(key)
            if neighbors:
                last = distance_to(neighbors[-1].id, key)
                new_node_close = distance_to(node.id, key) < last
                first = distance_to(neighbors[0].id, key)
                this_closest = distance_to(self.id, key) < first
            if not neighbors or (new_node_close and this_closest):
                self.call_store(node, key, value)
        self.router.add(node)

    def lookup(self, id):
        """Realiza una búsqueda para encontrar los k nodos más cercanos a un ID"""

        log.info(f"Initiating lookup for key {id}")
        node = KademliaNodeData(id=id)

        # Inicializar el conjunto de nodos más cercanos a partir de la tabla de enrutamiento
        nearest = SortedList(
            [
                (distance_to(id, contact.id), contact)
                for contact in self.router.k_closest_to(node.id)
            ]
        )
        if not nearest:
            log.warning(f"No known neighbors to lookup key {id}")
            return []

        # Iniciar las consultas a los alpha nodos más cercanos
        already_queried = set()
        already_inserted = set()
        results = []

        def call_find_node_and_save(n, id):
            results.append(self.call_find_node(n, id))

        while True:
            # Seleccionamos hasta alpha nodos para consultar simultáneamente
            threads = []
            for _, n in nearest:
                if not n.id in already_queried:
                    thread = Thread(target=call_find_node_and_save, args=(n, node.id))
                    threads.append(thread)
                    thread.start()
                    already_queried.add(n.id)

            for thread in threads:
                thread.join()

            for result in results:
                if result:
                    for n in result:
                        if (n.id not in already_queried) and (
                            n.id not in already_inserted
                        ):
                            nearest.add((distance_to(n.id, id), n))
                            already_inserted.add(n.id)

            del nearest[self.ksize :]
            if all(x.id in already_queried for _, x in nearest):
                break

        return [contact for _, contact in nearest]

    def bootstrap(self, nodes: List[KademliaNodeData]):
        """Realiza el bootstrap del nodo utilizando las direcciones iniciales"""
        log.debug(f"Attempting to bootstrap node with {len(nodes)} initial contacts")
        threads = []
        for node in nodes:
            thread = Thread(target=self.router.add, args=(node,))
            threads.append(thread)
            thread.start()
            thread = Thread(target=self.call_ping, args=(node,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        self.lookup(self.id)
        self.router.poblate()

    def set(self, key, value):
        """Almacena un valor en la red"""
        log.info(f"Setting '{key}' = '{value}' on network")
        dkey = digest_to_int(key, num_bits=N_OF_BITS)
        closest = self.lookup(dkey)
        threads = []
        for contact in closest:
            thread = Thread(target=self.call_store, args=(contact, dkey, value))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return True

    def get(self, dkey):
        """Busca un valor en la red"""
        log.info(f"Looking up key {dkey}")
        dkey = digest_to_int(dkey, num_bits=N_OF_BITS)
        closest = self.lookup(dkey)
        results = []

        def call_find_value_and_save(contact, dkey):
            results.append(self.call_find_value(contact, dkey))

        threads = []
        for contact in closest:
            thread = Thread(target=call_find_value_and_save, args=(contact, dkey))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for result, is_value in results:
            if is_value:
                return result
        return False
        """
        dict_results = {}
        for result, is_value in results:
            if is_value:
                dict_results[result] = dict_results.get(result, 0) + 1
        dict_results = list(dict_results.items())
        return (
            max(dict_results, key=lambda tpl: tpl[1])[0]
            if len(dict_results) > 0
            else False
        )
        """

    def bootstrappable_k_closest(self):
        return self.router.k_closest_to(self.node_data.id)

    def save_state(self, fname):
        """Guarda el estado del nodo en un archivo"""
        log.info(f"Saving state to {fname}")
        # Obtener la ruta del archivo actual y agregar el subdirectorio/nombre de archivo
        base_path = os.path.dirname(os.path.abspath(__file__))
        fname = os.path.join(base_path, fname)

        # Asegurarse de que el directorio exista
        directory = os.path.dirname(fname)
        if not os.path.exists(directory):
            os.makedirs(directory)
        data = {
            "ksize": self.ksize,
            "alpha": self.alpha,
            "id": self.id,
            "storage": self.storage,
            "neighbors": self.bootstrappable_k_closest(),
        }
        with open(fname, "wb") as f:
            try:
                pickle.dump(data, f)
            except Exception as e:
                log.error(f"Error saving component: {e}")

    @classmethod
    def load_state(cls, fname, port, interface="0.0.0.0"):
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
        node.listen()
        if data["neighbors"]:
            node.bootstrap(data["neighbors"])
        return node


def distance_to(node_1_id, node_2_id):
    # Calcula la distancia de un nodo a otro nodo usando XOR
    return node_1_id ^ node_2_id
