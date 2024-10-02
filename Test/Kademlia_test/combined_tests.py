import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


import logging
import random
import threading


from src.kademlia_network.kademlia_node import KademliaNode
from src.kademlia_network.kademlia_node_data import KademliaNodeData


# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_bootstrapping():
    # Número de nodos en la red
    num_nodes = 15
    ksize = 2
    nodes = []

    # Creación de nodos
    for i in range(num_nodes):
        node = KademliaNode(node_id=i, ip="127.0.0.1", port=60000 + i, ksize=ksize)
        node.listen()
        nodes.append(node)

    # Bootstrap de la red
    bootstrap_nodes = [
        KademliaNodeData(ip=node.host, port=node.port, id=node.id) for node in nodes
    ]

    def bootstrap_node(node, bootstrap_nodes):
        node.bootstrap([n for n in bootstrap_nodes if n.id != node.id])

    threads = []
    for node in nodes:
        thread = threading.Thread(target=bootstrap_node, args=(node, bootstrap_nodes))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    #  Verificar que todos los nodos tienen al menos un vecino
    for node in nodes:
        closest_nodes = node.router.k_closest_to(node.id)
        assert (
            len(closest_nodes) > 0
        ), f"El nodo {node.id} no tiene vecinos cercanos después del bootstrap"

    # Test simple de set y get
    test_key = "clave_prueba"
    test_value = "valor_prueba"
    nodes[0].set(test_key, test_value)

    retrieved_value = nodes[1].get(test_key)
    assert (
        retrieved_value == test_value
    ), "El valor recuperado no coincide con el valor almacenado"

    # Test con claves y valores complejos
    complex_key = "key_with_special_chars_!@#$%^&*()"
    complex_value = "value_with_special_chars_{}[]|\\<>"
    nodes[5].set(complex_key, complex_value)

    retrieved_value = nodes[10].get(complex_key)
    assert (
        retrieved_value == complex_value
    ), "El valor complejo recuperado no coincide con el valor almacenado"

    # Simular fallo de nodo y verificar operación
    nodes[0].storage.clear()
    nodes[1].set("key_falla", "value_falla")
    retrieved_value = nodes[2].get("key_falla")
    assert (
        retrieved_value == "value_falla"
    ), "El sistema no manejó correctamente el fallo del nodo"

    # Test de alto volumen
    test_data = {f"key_{i}": f"value_{i}" for i in range(100)}

    def set_data(key, value):
        nodes[0].set(key, value)

    threads = []
    for key, value in test_data.items():
        thread = threading.Thread(target=set_data, args=(key, value))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for key, value in test_data.items():
        retrieved_value = nodes[random.randint(1, 14)].get(key)
        assert (
            retrieved_value == value
        ), f"Fallo al recuperar el valor para la clave {key}"
        # * Aki falla pero es por que ocurren colisiones debido  una baja canFtidad de bits

    print("Todos los tests pasaron correctamente.")


if __name__ == "__main__":
    test_bootstrapping()
