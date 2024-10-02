import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


import logging

from src.kademlia_network.kademlia_node import KademliaNode


# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_call_ping():
    node1 = KademliaNode(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = KademliaNode(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    node3 = KademliaNode(node_id=2, ip="127.0.0.1", port=8003, ksize=2)
    node3.listen()

    result = node2.call_ping(node1.node_data)
    result1 = node1.call_ping(node2.node_data)
    result2 = node2.call_ping(node1.node_data)

    assert result, f"El nodo {node2.id} no oobtuvo respuesta al ping hacia {node1.id}"

    assert result1, f"El nodo {node1.id} no oobtuvo respuesta al ping hacia {node2.id}"

    assert result2, f"El nodo {node2.id} no oobtuvo respuesta al ping hacia {node1.id}"

    log.info("Test ping sucess")


if __name__ == "__main__":
    test_call_ping()
