from src.kademlia_network.kademlia_list_node import KademliaListNode
from src.Interfaces.IStorage import IStorage
from flask import request, jsonify
from typing import Tuple


class EmptyQueueException(Exception):
    pass


class KademliaQueueNode(KademliaListNode):
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
        self.configure_queue_endpoints()

    def configure_queue_endpoints(self):
        @self.app.route("/leader/pop")
        def pop_as_leader():
            data = request.get_json(force=True)
            queue = data.get("queue")
            response = self.pop_as_leader(queue)
            return jsonify(response), 200

    def pop_as_leader(self, queue):
        first_idx = self.get_first_idx(queue)
        if first_idx == self.get_length(queue):
            raise EmptyQueueException(f"{queue} is empty")
        value = self.list_get(queue, first_idx)
        self.set_first_idx(queue, first_idx + 1)
        return {"status": "OK", "value": value}

    def push(self, queue, value):
        self.append(queue, value)

    def pop(self, queue):
        address = self.find_leader_address()
        data = {"queue": queue}
        response = self.call_rpc(address, "/leader/pop", data)
        if response is None:
            print(f"No response from node {address}")
            return False
        return response.get("status") == "OK"

    def get_first_idx(self, queue):
        first_idx = self.get(f"{queue}_first")
        if first_idx == False:
            return 0
        return first_idx

    def set_first_idx(self, queue, idx):
        self.set(f"{queue}_first", idx)