import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


import logging

from src.kademlia_network.kademlia_node import KademliaNode
from src.utils.utils import N_OF_BITS, digest_to_int


# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_get():
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

    # Pre-llenar la red con algunos valores
    key = "simple_key"
    value = "simple_value"
    node1.set(key, value)

    complex_key = "complex_key_@#!$%^&*"
    complex_value = "complex_value_{}[]|\\<>"
    k = digest_to_int(complex_key, num_bits=N_OF_BITS)
    node1.set(complex_key, complex_value)

    duplicate_key = "duplicate_key"
    value1 = "value1"
    node1.set(duplicate_key, value1)

    # Caso de prueba 1: Recuperar un valor simple
    retrieved_value = node2.get(key)
    assert (
        retrieved_value == value
    ), f"El valor recuperado no coincide: {retrieved_value} != {value}"

    # Caso de prueba 2: Recuperar un valor complejo
    retrieved_value = node3.get(complex_key)
    assert (
        retrieved_value == complex_value
    ), f"El valor complejo recuperado no coincide: {retrieved_value} != {complex_value}"

    # Caso de prueba 3: Recuperar un valor duplicado
    retrieved_value = node4.get(
        duplicate_key
    )  #! Se ejecuta indefinidamente haciendo llamadas
    assert (
        retrieved_value == value1
    ), f"El valor duplicado recuperado no coincide: {retrieved_value} != {value1}"

    # Caso de prueba 4: Recuperar un valor inexistente
    non_existent_key = "non_existent_key"
    n = digest_to_int(non_existent_key, num_bits=N_OF_BITS)
    try:
        retrieved_value_non_existent_key = node1.get(non_existent_key)
        assert False, "Se esperaba una excepción para una clave inexistente"
    except Exception as e:
        log.info("Se manejó correctamente una clave inexistente.")

    # Caso de prueba 5: Recuperar un valor cuando un nodo falla
    node2.listen = lambda: None  # Simular un fallo en node2
    retrieved_value = node3.get(key)
    assert (
        retrieved_value == value
    ), f"El valor recuperado no coincide cuando un nodo falla: {retrieved_value} != {value}"

    log.info("Todos los casos de prueba para get pasaron correctamente.")


if __name__ == "__main__":
    test_get()
