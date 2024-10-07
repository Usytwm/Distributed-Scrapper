from flask import jsonify, request
from src.Interfaces.WorkerNode import Worker_Node
from src.utils.utils import NodeType


class StorageNode(Worker_Node):
    def __init__(self, host, port, id=None):
        super().__init__(id=id, host=host, port=port, role=NodeType.STORAGE.value)
        self.configure_storage_endpoint()

    def configure_storage_endpoint(self):
        @self.app.route("/set", methods=["POST"])
        def set():
            data = request.get_json(force=True)
            key, value, redirection = (
                data.get("key"),
                data.get("value"),
                data.get("redirection"),
            )
            response = self.set(key, value)
            redirectiron_response = (
                self.set(redirection, value) if redirection else None
            )
            combined_response = {
                "status": "OK",
            }

            return jsonify(combined_response), 200

        @self.app.route("/get", methods=["POST"])
        def get():
            data = request.get_json(force=True)
            key = data.get("key")
            response = self.get(key)
            if not response:
                return jsonify({"status": "OK", "value": None}), 200
            response = {"status": "OK", "value": response}
            return jsonify(response), 200


def set(self, key, value):
    self.set(key, value)
    return {"status": "OK"}


def get(self, key):
    value = self.get(key)
    if not (value == False):
        return {"status": "OK", "value": value}
    else:
        return {"status": "OK", "value": None}
