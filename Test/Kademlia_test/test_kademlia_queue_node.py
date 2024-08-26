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
    # storage1 = Storage(ttl=10)
    node1 = KademliaQueueNode(node_id=1, ip="127.0.0.1", port=8001, ksize=4)
    node1.listen()

    # storage2 = Storage(ttl=10)
    node2 = KademliaQueueNode(node_id=2, ip="127.0.0.1", port=8002, ksize=4)
    node2.listen()

    # storage3 = Storage(ttl=10)
    node3 = KademliaQueueNode(node_id=3, ip="127.0.0.1", port=8003, ksize=4)
    node3.listen()

    # storage4 = Storage(ttl=10)
    node4 = KademliaQueueNode(node_id=4, ip="127.0.0.1", port=8004, ksize=4)
    node4.listen()

    node1.bootstrap([node2.node_data, node3.node_data, node4.node_data])

    queue = "test_queue"
    value = "value"
    queue1 = "test_queue1"
    value1 = "value1"

    node1.push(queue, "queue_test1")
    node2.push(queue1, value1)
    node2.push(queue, "queue_test2")
    node3.push(queue1, value1)
    node4.push(queue, "queue_test3")
    node2.push(queue1, value1)

    result1 = node4.pop(queue)
    # result1 = node1.pop(queue1)
    result2 = node3.pop(queue)
    # result1 = node2.pop(queue1)
    result3 = node1.pop(queue)
    # result1 = node2.pop(queue1)
    result4 = node3.pop(queue)

    log.info("Todos los casos de prueba para KademliaQueueNode pasaron correctamente.")


if __name__ == "__main__":
    test_kademlia_queue_node()
