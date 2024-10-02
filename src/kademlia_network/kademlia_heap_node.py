import logging
from src.kademlia_network.kademlia_list_node import KademliaListNode
from src.Interfaces.IStorage import IStorage
from flask import request, jsonify
from typing import Tuple

log = logging.getLogger(__name__)


class EmptyHeapException(Exception):
    pass


class KademliaHeapNode(KademliaListNode):
    def __init__(
        self,
        node_id=None,
        storage: IStorage = None,
        ip=None,
        port=None,
        ksize: int = 20,
        alpha=3,
        max_chunk_size=2,
    ):
        super().__init__(node_id, storage, ip, port, ksize, alpha)
        self.max_chunk_size = max_chunk_size
        self.configure_heap_endpoints()

    def configure_heap_endpoints(self):
        @self.app.route("/leader/init_heap", methods=["POST"])
        def init_heap_as_leader():
            data = request.get_json(force=True)
            heap = data.get("heap")
            response = self.init_heap_as_leader(heap)
            return jsonify(response), 200

        @self.app.route("/leader/pop", methods=["POST"])
        def pop_as_leader():
            data = request.get_json(force=True)
            heap = data.get("heap")
            response = self.pop_as_leader(heap)
            return jsonify(response), 200

    def init_heap_as_leader(self, heap):
        self.init_list_as_leader(heap)

    def pop_as_leader(self, heap):
        length = self.get_length(heap)
        if length == 0:
            raise {"status": "OK", "value": None}
        value = self.list_get(heap, length)
        self.set_length(heap, length - 1)
        return {"status": "OK", "value": value}

    def init_heap(self, heap):
        address = self.find_leader_address()
        data = {"heap": heap}
        response = self.call_rpc(address, "/leader/init_heap", data)
        if response is None:
            log.debug(f"No response from node {address}")
            return False
        return response.get("status") == "OK"

    def push(self, heap, value):
        return self.append(heap, value)

    def pop(self, heap):
        address = self.find_leader_address()
        data = {"heap": heap}
        response = self.call_rpc(address, "/leader/pop", data)
        if response is None:
            log.debug(f"No response from node {address}")
            return None
        return response.get("value")
