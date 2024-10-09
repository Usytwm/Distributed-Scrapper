import logging
from src.kademlia_network.kademlia_list_node import KademliaListNode
from src.Interfaces.IStorage import IStorage
from flask import request, jsonify
from typing import Tuple

log = logging.getLogger(__name__)


class EmptyQueueException(Exception):
    pass


class KademliaQueueNode(KademliaListNode):
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
        self.configure_queue_endpoints()

    def configure_queue_endpoints(self):
        @self.app.route("/leader/init_queue", methods=["POST"])
        def init_queue_as_leader():
            data = request.get_json(force=True)
            queue = data.get("queue")
            response = self.init_queue_as_leader(queue)
            return jsonify(response), 200

        @self.app.route("/leader/pop", methods=["POST"])
        def pop_as_leader():
            data = request.get_json(force=True)
            queue = data.get("queue")
            response = self.pop_as_leader(queue)
            return jsonify(response), 200

    def init_queue_as_leader(self, queue):
        self.init_list_as_leader(queue)
        self.set_first_idx(queue, 0)

    def pop_as_leader(self, queue):
        first_idx = self.get_first_idx(queue)
        if first_idx == self.get_length(queue):
            return {"status": "OK", "value": None}
        value = self.list_get(queue, first_idx)
        # log.warning(f"Pop value {value} from {queue}")
        self.set_first_idx(queue, first_idx + 1)
        return {"status": "OK", "value": value}

    def init_queue(self, queue):
        address = self.find_leader_address()
        data = {"queue": queue}
        response = self.call_rpc(address, "/leader/init_queue", data)
        if response is None:
            log.debug(f"No response from node {address}")
            return False
        return response.get("status") == "OK"

    def push(self, queue, value):
        return self.append(queue, value)

    def pop(self, queue):
        address = self.find_leader_address()
        data = {"queue": queue}
        response = self.call_rpc(address, "/leader/pop", data)
        if response is None:
            log.debug(f"No response from node {address}")
            return None
        return response.get("value")

    def get_first_idx(self, queue):
        first = self.get(f"{queue}_first")
        # if queue == "urls":
        #     log.critical(f"Get first idx {first if first != False else 0} from {queue}")
        return first if first != False else 0

    def set_first_idx(self, queue, idx):
        self.set(f"{queue}_first", idx)

    def is_empty(self, queue):
        return self.get_length(queue) == self.get_first_idx(queue)

    def get_length_queue(self, queue):
        return self.get_length(queue) - self.get_first_idx(queue)
