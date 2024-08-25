import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


import logging

from src.kademlia_network.kademlia_node import KademliaNode


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_call_find_node():
    node1 = KademliaNode(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = KademliaNode(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    node3 = KademliaNode(node_id=3, ip="127.0.0.1", port=8003, ksize=2)
    node3.listen()

    # Agregar los nodos directamente a la tabla de enrutamiento de node1
    node1.router.add(node2.node_data)
    node1.router.add(node3.node_data)

    # También puedes agregar los nodos a las tablas de enrutamiento de node2 y node3
    node2.router.add(node1.node_data)
    node2.router.add(node3.node_data)

    node3.router.add(node1.node_data)
    node3.router.add(node2.node_data)

    # Intentar encontrar los nodos más cercanos al ID de node3 desde node1
    closest_nodes = node1.call_find_node(node2.node_data, node3.id)

    assert (
        len(closest_nodes) > 0
    ), f"El nodo {node1.id} no pudo encontrar nodos cercanos al ID {node3.id}"
    assert (
        node3.node_data in closest_nodes
    ), f"El nodo {node3.id} no fue encontrado como el más cercano"

    log.info("Test call_find_node passed")


if __name__ == "__main__":
    test_call_find_node()
