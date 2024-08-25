import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


import logging
from src.kademlia_network.kademlia_node import KademliaNode
from src.utils.utils import N_OF_BITS, digest_to_int


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_set():
    # Configuración de la red
    node1 = KademliaNode(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = KademliaNode(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    node3 = KademliaNode(node_id=3, ip="127.0.0.1", port=8003, ksize=2)
    node3.listen()

    node4 = KademliaNode(node_id=4, ip="127.0.0.1", port=8004, ksize=2)
    node4.listen()

    node1.bootstrap([node2.node_data, node3.node_data, node4.node_data])

    # Caso de prueba 1: Almacenar un valor simple
    key = "simple_key"
    value = "simple_value"
    assert node1.set(key, value), "Fallo al almacenar un valor simple en la red"

    # Verificar que el valor se almacena correctamente en los nodos más cercanos
    stored_value = node4.storage.get(digest_to_int(key, num_bits=N_OF_BITS))
    assert (
        stored_value == value
    ), f"El valor almacenado no coincide en node4: {stored_value} != {value}"

    # Caso de prueba 2: Almacenar un valor complejo
    complex_key = "complex_key_@#!$%^&*"
    complex_value = "complex_value_{}[]|\\<>"
    assert node1.set(
        complex_key, complex_value
    ), "Fallo al almacenar un valor complejo en la red"

    stored_value = node3.storage.get(digest_to_int(complex_key, num_bits=N_OF_BITS))
    assert (
        stored_value == complex_value
    ), f"El valor almacenado no coincide en node3: {stored_value} != {complex_value}"

    # Caso de prueba 3: Almacenar valores duplicados
    duplicate_key = "duplicate_key"
    value1 = "value1"
    value2 = "value2"
    assert node1.set(
        duplicate_key, value1
    ), "Fallo al almacenar el primer valor duplicado en la red"
    assert node1.set(
        duplicate_key, value2
    ), "Fallo al almacenar el segundo valor duplicado en la red"

    stored_value = node4.storage.get(digest_to_int(duplicate_key, num_bits=N_OF_BITS))
    assert (
        stored_value == value2
    ), f"El valor almacenado no coincide en node4: {stored_value} != {value2}"

    # Caso de prueba 4: Almacenar un valor cuando un nodo falla
    node4.listen = lambda: None  # Simular un fallo en node4
    failed_key = "failed_key"
    failed_value = "failed_value"
    assert node1.set(
        failed_key, failed_value
    ), "Fallo al almacenar un valor cuando un nodo falla"
    value = digest_to_int(failed_key, num_bits=N_OF_BITS)
    stored_value = node4.storage.get(value)
    assert (
        stored_value == failed_value
    ), f"El valor almacenado no coincide en node4 cuando un nodo falla: {stored_value} != {failed_value}"

    log.info("Todos los casos de prueba para set pasaron correctamente.")


if __name__ == "__main__":
    test_set()
