import sys
from pathlib import Path
import time
import logging


path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


from src.kademlia_network.kademlia_node import KademliaNode
from src.utils.utils import N_OF_BITS, digest_to_int
from src.kademlia_network.kademlia_queue_node import KademliaQueueNode
from src.kademlia_network.storage import Storage


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_kademlia_queue_node():
    # Configuración de la red con almacenamiento real
    node1 = KademliaQueueNode(node_id=1, ip="127.0.0.1", port=8001, ksize=4)
    node1.listen()

    node2 = KademliaQueueNode(node_id=2, ip="127.0.0.1", port=8002, ksize=4)
    node2.listen()

    node3 = KademliaQueueNode(node_id=3, ip="127.0.0.1", port=8003, ksize=4)
    node3.listen()

    node4 = KademliaQueueNode(node_id=4, ip="127.0.0.1", port=8004, ksize=4)
    node4.listen()

    node1.bootstrap([node2.node_data, node3.node_data, node4.node_data])

    queue = "test_queue"

    # Caso de prueba 1: Insertar un solo elemento en la cola y luego eliminarlo
    node1.push(queue, "single_element")
    result = node1.pop(queue)
    assert result == "single_element", f"Error en el test de un solo elemento: {result}"

    # Caso de prueba 2: Insertar múltiples elementos en la cola y eliminarlos en orden
    elements = ["element1", "element2", "element3"]
    for elem in elements:
        node1.push(queue, elem)

    for elem in elements:
        result = node1.pop(queue)
        assert result == elem, f"Error en el test de múltiples elementos: {result}"

    # Caso de prueba 3: Insertar elementos hasta que se cree un nuevo chunk
    for i in range(1, 5):
        node1.push(queue, f"chunk_test_{i}")

    for i in range(1, 5):
        result = node1.pop(queue)
        assert (
            result == f"chunk_test_{i}"
        ), f"Error en el test de creación de chunk: {result}"

    # Caso de prueba 4: Insertar y eliminar intercaladamente
    node1.push(queue, "intercalate1")
    node1.push(queue, "intercalate2")
    result1 = node1.pop(queue)
    node1.push(queue, "intercalate3")
    result2 = node1.pop(queue)
    result3 = node1.pop(queue)

    assert result1 == "intercalate1", f"Error en el test de intercalado 1: {result1}"
    assert result2 == "intercalate2", f"Error en el test de intercalado 2: {result2}"
    assert result3 == "intercalate3", f"Error en el test de intercalado 3: {result3}"

    # Caso de prueba 5: Eliminar de una cola vacía
    result = node1.pop(queue)
    assert result == None, f"Error en el test de cola vacía: {result}"

    # Caso de prueba 6: Crear múltiples colas en diferentes nodos y verificar la integridad
    node1.push("queue1", "node1_queue1_value")
    node2.push("queue2", "node2_queue2_value")
    node3.push("queue3", "node3_queue3_value")
    node4.push("queue4", "node4_queue4_value")

    result1 = node1.pop("queue1")
    result2 = node2.pop("queue2")
    result3 = node3.pop("queue3")
    result4 = node4.pop("queue4")

    assert (
        result1 == "node1_queue1_value"
    ), f"Error en el test de múltiples colas 1: {result1}"
    assert (
        result2 == "node2_queue2_value"
    ), f"Error en el test de múltiples colas 2: {result2}"
    assert (
        result3 == "node3_queue3_value"
    ), f"Error en el test de múltiples colas 3: {result3}"
    assert (
        result4 == "node4_queue4_value"
    ), f"Error en el test de múltiples colas 4: {result4}"

    # Caso de prueba 7: Insertar más elementos de los que puede manejar un chunk
    for i in range(10):
        node1.push(queue, f"overflow_test_{i}")

    for i in range(10):
        result = node1.pop(queue)
        assert (
            result == f"overflow_test_{i}"
        ), f"Error en el test de overflow de chunk: {result}"

    # Caso de prueba 8: Eliminar hasta vaciar todos los chunks
    node1.push(queue, "final_test1")
    node1.push(queue, "final_test2")
    node1.push(queue, "final_test3")
    node1.push(queue, "final_test4")

    assert node1.pop(queue) == "final_test1", "Error en el test final 1"
    assert node1.pop(queue) == "final_test2", "Error en el test final 2"
    assert node1.pop(queue) == "final_test3", "Error en el test final 3"
    assert node1.pop(queue) == "final_test4", "Error en el test final 4"
    assert node1.pop(queue) == None, "Error en el test de vaciado final"

    log.info("Todos los casos de prueba para KademliaQueueNode pasaron correctamente.")


if __name__ == "__main__":
    test_kademlia_queue_node()
