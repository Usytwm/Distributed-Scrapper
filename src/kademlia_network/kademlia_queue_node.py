from kademlia_node import KademliaNode
from src.Interfaces.IStorage import IStorage
from flask import request, jsonify


class KademliaQueueNode(KademliaNode):
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
        self.init_new_endpoints()

    def init_new_endpoints(self):
        @self.app.route("/push_as_leader")
        def push_as_leader():
            data = request.get_json(force=True)
            queue, value = data.get("queue"), data.get("value")
            response = self.push_as_leader(queue, value)
            return jsonify(response), 200

        @self.app.route("/pop_as_leader")
        def pop_as_leader():
            data = request.get_json(force=True)
            queue = data.get("queue")
            response = self.pop_as_leader(queue)
            return jsonify(response), 200

    def push_as_leader(self, queue, value):
        response = self.get(f"{queue}_current_chunks")
        if response == False:
            response = (0, 0)
            self.set(f"{queue}_current_chunks", response)
            self.set(f"{queue}_chunk_{0}", [])
        start_idx, end_idx = response
        chunk = self.get(f"{queue}_chunk_{end_idx}")
        chunk.append(value)
        self.set(f"{queue}_chunk_{end_idx}", chunk)
        if len(chunk) == self.max_chunk_size:
            self.set(f"{queue}_current_chunks", (start_idx, end_idx + 1))
            self.set(f"{queue}_chunk_{end_idx + 1}", [])
        return {"status": "OK"}

    def pop_as_leader(self, queue):
        response = self.get(f"{queue}_current_chunks")
        if response == False:
            return {"status": "OK", "value": None}
        start_idx, end_idx = response
        chunk = self.get(f"{queue}_chunk_{start_idx}")
        answer = chunk[0]
        chunk = chunk[1:]
        self.set(f"{queue}_chunk_{start_idx}", chunk)
        if len(chunk) == 0:
            self.set(f"{queue}_current_chunks", (start_idx + 1, end_idx))
        return {"status": "OK", "value": answer}

    def find_leader(self):
        return self.lookup(0)[0]

    def push(self, queue, value):
        leader = self.find_leader()
        address = f"{leader.ip}:{leader.port}"
        data = {"queue": queue, "value": value}
        response = self.call_rpc(address, "push_as_leader", data)
        if response is None:
            print(f"No response from node {address}")
            return False

        return response.get("status") == "OK"

    def pop(self, queue):
        leader = self.find_leader()
        address = f"{leader.ip}:{leader.port}"
        data = {"queue": queue}
        response = self.call_rpc(address, "push_as_leader", data)
        if response is None:
            print(f"No response from node {address}")
            return False

        return response.get("status") == "OK"
