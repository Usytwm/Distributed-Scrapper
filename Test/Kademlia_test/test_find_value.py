import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


import logging

from src.kademlia_network.kademlia_node import KademliaNode
from src.utils.utils import N_OF_BITS, digest_to_int


# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_call_find_value():
    node1 = KademliaNode(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = KademliaNode(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    # Almacenar un valor en node2
    key = digest_to_int("test_key", num_bits=N_OF_BITS)
    value = "test_value"
    node2.storage[key] = value

    # Intentar recuperar el valor desde node1
    retrieved_value, is_value = node1.call_find_value(node2.node_data, key)

    assert (
        is_value
    ), f"El nodo {node1.id} no pudo recuperar la clave '{key}' desde el nodo {node2.id}"
    assert (
        retrieved_value == value
    ), f"El valor recuperado '{retrieved_value}' no coincide con el valor esperado '{value}'"

    log.info("Test call_find_value passed")


if __name__ == "__main__":
    test_call_find_value()
