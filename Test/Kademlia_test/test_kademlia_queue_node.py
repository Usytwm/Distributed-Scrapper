import sys
from pathlib import Path
import time

from src.kademlia_network.kademlia_queue_node import KademliaQueueNode

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


import logging

from src.kademlia_network.kademlia_node import KademliaNode
from src.utils.utils import N_OF_BITS, digest_to_int


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_kademlia_queue_node():
    # Configuración de la red con almacenamiento real
    storage1 = Storage(ttl=10)
    node1 = KademliaQueueNode(
        node_id=1, storage=storage1, ip="127.0.0.1", port=8001, ksize=2
    )
    node1.listen()

    storage2 = Storage(ttl=10)
    node2 = KademliaQueueNode(
        node_id=2, storage=storage2, ip="127.0.0.1", port=8002, ksize=2
    )
    node2.listen()

    storage3 = Storage(ttl=10)
    node3 = KademliaQueueNode(
        node_id=3, storage=storage3, ip="127.0.0.1", port=8003, ksize=2
    )
    node3.listen()

    storage4 = Storage(ttl=10)
    node4 = KademliaQueueNode(
        node_id=4, storage=storage4, ip="127.0.0.1", port=8004, ksize=2
    )
    node4.listen()

    node1.bootstrap([node2.node_data, node3.node_data, node4.node_data])

    # Caso de prueba 1: push_as_leader y verificar almacenamiento
    queue = "test_queue"
    value1 = "value1"
    assert node1.push_as_leader(queue, value1) == {
        "status": "OK"
    }, "Fallo en push_as_leader"

    stored_value = node1.storage.get(f"{queue}_chunk_0")
    assert stored_value == [
        value1
    ], f"El valor almacenado no coincide en node1: {stored_value} != {[value1]}"

    # Caso de prueba 2: pop_as_leader y verificar el valor devuelto
    popped_value = node1.pop_as_leader(queue)
    assert popped_value == {
        "status": "OK",
        "value": value1,
    }, f"El valor devuelto no coincide: {popped_value} != {value1}"

    # Caso de prueba 3: Almacenar varios valores y verificar chunks
    value2 = "value2"
    value3 = "value3"
    node1.push_as_leader(queue, value1)
    node1.push_as_leader(queue, value2)
    node1.push_as_leader(queue, value3)

    # Verificar que el chunk se haya dividido correctamente
    stored_chunk_0 = node1.storage.get(f"{queue}_chunk_0")
    stored_chunk_1 = node1.storage.get(f"{queue}_chunk_1")
    assert stored_chunk_0 == [
        value1,
        value2,
    ], f"El chunk 0 no coincide: {stored_chunk_0} != {[value1, value2]}"
    assert stored_chunk_1 == [
        value3
    ], f"El chunk 1 no coincide: {stored_chunk_1} != {[value3]}"

    # Caso de prueba 4: Verificar que los valores se eliminen después del TTL
    time.sleep(11)
    assert (
        node1.storage.get(f"{queue}_chunk_0") == None
    ), "El chunk 0 no se eliminó después del TTL"
    assert (
        node1.storage.get(f"{queue}_chunk_1") == None
    ), "El chunk 1 no se eliminó después del TTL"

    log.info("Todos los casos de prueba para KademliaQueueNode pasaron correctamente.")


if __name__ == "__main__":
    test_kademlia_queue_node()
