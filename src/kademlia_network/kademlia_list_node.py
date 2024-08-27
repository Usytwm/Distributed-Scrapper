from kademlia_node import KademliaNode
from src.Interfaces.IStorage import IStorage
from flask import request, jsonify
from typing import Tuple, List


class KademliaListNode(KademliaNode):
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
        self.configure_list_endpoints()

    def configure_list_endpoints(self):
        @self.app.route("/leader/append", methods=["POST"])
        def append_as_leader():
            data = request.get_json(force=True)
            list, value = data.get("list"), data.get("value")
            response = self.append_as_leader(list, value)
            return jsonify(response), 200

        @self.app.route("/leader/list_set", methods=["POST"])
        def list_set_as_leader():
            data = request.get_json(force=True)
            list, value = data.get("list"), data.get("value")
            response = self.append_as_leader(list, value)
            return jsonify(response), 200

    def append_as_leader(self, list, value):
        length, chunk_idx, chunk = self.get_tail(list)
        chunk.append(value)
        self.set_chunk(list, chunk_idx, chunk)
        length += 1
        self.set_length(list, length)
        if (length % self.max_chunk_size) == 0:
            self.set_chunk(list, chunk_idx + 1, [])

    def list_set_as_leader(self, list, idx, value):
        chunk_idx, idx_in_chunk, chunk = self.chunk_for_idx(list, idx)
        chunk[idx_in_chunk] = value
        self.set_chunk(list, chunk_idx, idx_in_chunk)

    def find_leader_address(self) -> str:
        leader = self.lookup(0)[0]
        return f"{leader.ip}:{leader.port}"

    def append(self, list, value):
        address = self.find_leader_address()
        data = {"list": list, "value": value}
        response = self.call_rpc(address, "leader/append", data)
        if response is None:
            print(f"No response from node {address}")
            return
        return response.get("status") == "OK"

    def list_set(self, list, index, value):
        address = self.find_leader_address()
        data = {"list": list, "idx": index, "value": value}
        response = self.call_rpc(address, "leader/list_set", data)
        if response is None:
            print(f"No response from node {address}")
            return
        return response.get("status") == "OK"

    def list_get(self, list, index):
        _, idx_in_chunk, chunk = self.chunk_for_idx(list, index)
        return chunk[idx_in_chunk]

    def get_tail(self, list) -> Tuple[int, int, List]:
        """Devuelve la longitud de la cola,
        el indice del ultimo chunk,
        y el ultimo chunk"""
        length = self.get(f"{list}_length")
        chunk_idx, _, chunk = self.chunk_for_idx()
        if chunk == False:
            chunk = []
        return length, chunk_idx, chunk

    def chunk_for_idx(self, list, idx) -> Tuple[int, int, List]:
        """Dado un id devuelve:
        El indice del chunk en el que se encuentra,
        la posicion en que se encuentra dentro de ese chunk
        y el chunk en si"""
        chunk_idx, idx_in_chunk = idx // self.max_chunk_size, idx % self.max_chunk_size
        chunk = self.get_chunk(list, chunk_idx)
        if chunk == False:
            raise IndexError()
        return chunk_idx, idx_in_chunk, chunk

    def set_chunk(self, list, chunk_idx, chunk):
        self.set(f"{list}_chunk_{chunk_idx}", chunk)

    def get_chunk(self, list, chunk_idx):
        return self.get(f"{list}_chunk_{chunk_idx}")

    def set_length(self, list, length):
        self.set(f"{list}_length", length)

    def get_length(self, list):
        length = self.get(f"{list}_length")
        if length == False:
            return 0
        return length
