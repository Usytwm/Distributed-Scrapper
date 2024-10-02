import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


import logging
from src.kademlia_network.kademlia_node import KademliaNode, distance_to


# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_lookup():
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

    # Agregar nodos a la tabla de enrutamiento de node1
    node1.router.add(node2.node_data)
    node1.router.add(node3.node_data)
    node1.router.add(node4.node_data)
    node1.router.add(node5.node_data)

    # Caso de prueba 1: Buscar el propio ID de node1
    result = node1.lookup(node1.id)
    assert len(result) > 0, f"El nodo {node1.id} no encontró vecinos para su propio ID."

    # Caso de prueba 2: Buscar un nodo directamente conocido
    result = node1.lookup(node2.id)
    assert (
        len(result) > 0
    ), f"El nodo {node1.id} no encontró vecinos cercanos al ID {node2.id}"
    assert (
        node2.node_data in result
    ), f"El nodo {node2.id} no fue encontrado como el más cercano al buscar su propio ID"

    # Caso de prueba 3: Buscar un nodo que no está directamente en la tabla pero está cerca
    unknown_node_id = 6  # ID que no está directamente en la tabla
    result = node1.lookup(unknown_node_id)
    assert (
        len(result) > 0
    ), f"El nodo {node1.id} no pudo encontrar vecinos cercanos al ID {unknown_node_id}"
    # Verificar que los resultados contienen nodos cercanos
    closest = min(result, key=lambda x: distance_to(x.id, unknown_node_id))
    assert closest.id in [
        node2.id,
        node3.id,
        node4.id,
        node5.id,
    ], f"El nodo más cercano al ID {unknown_node_id} no fue correcto"

    # Caso de prueba 4: Buscar un nodo con un ID alto no directamente conocido
    high_node_id = 50  # Un ID arbitrariamente alto que no está en la tabla
    result = node1.lookup(high_node_id)
    assert (
        len(result) > 0
    ), f"El nodo {node1.id} no pudo encontrar vecinos cercanos al ID {high_node_id}"
    # Verificar que los resultados contienen nodos más cercanos al ID alto
    closest = min(result, key=lambda x: distance_to(x.id, high_node_id))
    assert closest.id in [
        node2.id,
        node3.id,
        node4.id,
        node5.id,
    ], f"El nodo más cercano al ID {high_node_id} no fue correcto"

    # Caso de prueba 5: Buscar un nodo en un espacio de IDs densamente poblado
    node7 = KademliaNode(node_id=7, ip="127.0.0.1", port=8006, ksize=2)
    node7.listen()
    node1.router.add(node7.node_data)

    result = node1.lookup(node7.id)
    assert (
        len(result) > 0
    ), f"El nodo {node1.id} no pudo encontrar vecinos cercanos al ID {node7.id}"
    assert (
        node5.node_data in result
    ), f"El nodo {node5.id} no fue encontrado como el más cercano"

    log.info("Todos los casos de prueba para lookup pasaron correctamente.")


if __name__ == "__main__":
    test_lookup()
