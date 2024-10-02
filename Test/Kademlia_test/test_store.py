import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


import logging

from src.kademlia_network.kademlia_node import KademliaNode


# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_call_store():
    node1 = KademliaNode(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = KademliaNode(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    key = "test_key"
    value = "test_value"

    result = node1.call_store(node2.node_data, key, value)

    assert (
        result
    ), f"El nodo {node1.id} no pudo almacenar la clave '{key}' en el nodo {node2.id}"

    # Verificar que el valor se almacenó en node2
    stored_value = node2.storage.get(key)
    assert (
        stored_value == value
    ), f"El valor almacenado en el nodo {node2.id} no coincide con el esperado"

    log.info("Test call_store passed")


if __name__ == "__main__":
    test_call_store()
