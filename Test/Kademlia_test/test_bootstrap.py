import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


import logging

from src.kademlia_network.kademlia_node import KademliaNode, distance_to


# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_bootstrap():
    # Crear nodos de la red
    node1 = KademliaNode(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = KademliaNode(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    node3 = KademliaNode(node_id=3, ip="127.0.0.1", port=8003, ksize=2)
    node3.listen()

    node4 = KademliaNode(node_id=4, ip="127.0.0.1", port=8004, ksize=2)
    node4.listen()

    node5 = KademliaNode(node_id=5, ip="127.0.0.1", port=8005, ksize=2)
    node5.listen()

    # Agregar nodos iniciales a node1 a través del bootstrap
    bootstrap_nodes = [
        node2.node_data,
        node3.node_data,
        node4.node_data,
        node5.node_data,
    ]
    node1.bootstrap(bootstrap_nodes)

    # Caso de prueba 1: Verificar que node1 tiene nodos en su tabla de enrutamiento
    closest_nodes = node1.router.k_closest_to(node1.id)
    assert (
        len(closest_nodes) > 0
    ), "La tabla de enrutamiento de node1 está vacía después del bootstrap"

    # Caso de prueba 2: Verificar que node1 tiene los nodos más cercanos en su tabla de enrutamiento
    for node in [node3, node2]:
        assert (
            node.node_data in closest_nodes
        ), f"El nodo {node.node_data.id} no fue encontrado en la tabla de enrutamiento de node1 después del bootstrap"

    # Caso de prueba 3: Verificar que la tabla de enrutamiento de node1 se ha llenado correctamente
    expected_contacts = sorted(
        [node2.node_data, node3.node_data],
        key=lambda x: distance_to(x.id, node1.id),
    )
    actual_contacts = sorted(closest_nodes, key=lambda x: distance_to(x.id, node1.id))
    assert (
        expected_contacts == actual_contacts
    ), "Los contactos en la tabla de enrutamiento de node1 no son los más cercanos esperados"

    # Caso de prueba 4: Verificar que poblate funcionó correctamente
    # Esto debería haber intentado llenar la tabla de enrutamiento con nodos adicionales
    node_count_before = len(node1.router.get_contacts())
    node1.router.poblate()
    node_count_after = len(node1.router.get_contacts())
    assert (
        node_count_after >= node_count_before
    ), "El proceso de poblate no llenó correctamente la tabla de enrutamiento"

    # Caso de prueba 5: Verificar que el nodo sigue funcionando después de múltiples bootstrap calls
    node6 = KademliaNode(node_id=6, ip="127.0.0.1", port=8006, ksize=2)
    node6.listen()
    node1.bootstrap([node6.node_data])

    closest_nodes = node1.router.k_closest_to(node1.id)
    assert (
        node3.node_data in closest_nodes
    ), "El nodo3 no fue encontrado en la tabla de enrutamiento de node1 después de realizar bootstrap adicional"

    log.info("Todos los casos de prueba para bootstrap pasaron correctamente.")


if __name__ == "__main__":
    test_bootstrap()
