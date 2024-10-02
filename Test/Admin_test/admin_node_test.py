import requests
import logging
import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


from src.scrapper.scrapper_node import Scrapper_Node
from src.storage.storage_node import StorageNode
from src.administration.admin_node import Admin_Node
from src.kademlia_network.kademlia_node_data import KademliaNodeData
from src.Interfaces.IStorage import IStorage

# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_global_ping():
    """
    Prueba para verificar que el nodo admin responde correctamente al ping.
    """
    admin_node = Admin_Node(node_id=1, ip="127.0.0.1", port=9000)
    admin_node.listen()

    response = requests.post("http://127.0.0.1:9000/global_ping")
    assert (
        response.status_code == 200
    ), "Fallo: Código de estado incorrecto para global_ping"
    assert (
        response.json().get("status") == "OK"
    ), "Fallo: Respuesta incorrecta para global_ping"

    log.info("Test global_ping pasado correctamente.")


def test_follower_register():
    """
    Prueba para registrar un nodo follower en el admin node.
    """
    admin_node = Admin_Node(node_id=1, ip="127.0.0.1", port=8000)
    admin_node.listen()

    # Crear un nodo follower de ejemplo
    follower_node_data = KademliaNodeData(ip="127.0.0.1", port=8001, id=2)

    # Simular la llamada para registrar un nodo follower
    data = {"role": "scrapper", "node": follower_node_data.to_json()}
    response = requests.post("http://127.0.0.1:8000/follower/register", json=data)

    assert (
        response.status_code == 200
    ), "Fallo: Código de estado incorrecto para follower_register"
    assert response.json().get("status") == "OK", "Fallo: Registro de follower fallido"

    log.info("Test follower_register pasado correctamente.")


def test_leader_register():
    """
    Prueba para registrar un nodo leader en el admin node.
    """
    admin_node = Admin_Node(node_id=1, ip="127.0.0.1", port=8003)
    admin_node.listen()

    # Crear un nodo leader de ejemplo
    leader_node_data = KademliaNodeData(ip="127.0.0.1", port=8002, id=3)

    # Simular la llamada para registrar un nodo leader
    data = {"role": "leader", "node": leader_node_data.to_json()}
    response = requests.post("http://127.0.0.1:8003/leader/register", json=data)

    assert (
        response.status_code == 200
    ), "Fallo: Código de estado incorrecto para leader_register"
    assert response.json().get("status") == "OK", "Fallo: Registro de leader fallido"

    log.info("Test leader_register pasado correctamente.")


def test_scrap_result_handling():
    """
    Prueba para verificar que el nodo admin maneja correctamente los resultados de scrapping.
    """
    admin_node = Admin_Node(node_id=1, ip="127.0.0.1", port=8004)
    admin_node.listen()

    # Crear un nodo scrapper de ejemplo
    scrapper_node_data = KademliaNodeData(ip="127.0.0.1", port=8005, id=4)

    # Simular el envío de un resultado de scrapping al nodo admin
    data = {
        "url": ["http://example.com"],
        "scrapper": scrapper_node_data.to_json(),
        "state": True,
        "depth": 1,
    }
    response = requests.post(
        "http://127.0.0.1:8004/leader/handle_scrap_result", json=data
    )

    assert (
        response.status_code == 200
    ), "Fallo: Código de estado incorrecto para handle_scrap_result"
    assert (
        response.json().get("status") == "OK"
    ), "Fallo: Manejo incorrecto del resultado de scrapping"

    log.info("Test scrap_result_handling pasado correctamente.")


def test_follower_scrap():
    """
    Prueba para verificar que el nodo follower realiza scrapping correctamente.
    """
    admin_node = Admin_Node(node_id=1, ip="127.0.0.1", port=8005)
    admin_node.listen()

    scrapper_node = Scrapper_Node(host="127.0.0.1", port=8006)
    scrapper_node.listen()
    storage_node = StorageNode(host="127.0.0.1", port=8007)
    storage_node.listen()

    # Simular la llamada para realizar scrapping desde un follower
    data = {
        "url": "http://example.com",
        "scrapper": scrapper_node.node_data.to_json(),
        "storage": storage_node.node_data.to_json(),
        "depth": 1,
    }
    response = requests.post("http://127.0.0.1:8005/follower/scrap", json=data)

    assert (
        response.status_code == 200
    ), "Fallo: Código de estado incorrecto para follower_scrap"

    value = storage_node.get("http://example.com")

    assert value is not None, "Fallo: No se pudo almacenar el resultado del scrapping"

    log.info("Test follower_scrap pasado correctamente.")


def test_leader_run_and_stop():
    """
    Prueba para verificar que el nodo leader puede iniciar y detenerse correctamente.
    """
    admin_node = Admin_Node(node_id=1, ip="127.0.0.1", port=8008)
    admin_node.listen()

    # Simular la llamada para iniciar el nodo leader
    response = requests.post("http://127.0.0.1:8008/leader/run")
    assert (
        response.status_code == 200
    ), "Fallo: Código de estado incorrecto para leader_run"
    assert response.json().get("status") == "OK", "Fallo: No se pudo iniciar el leader"

    # Simular la llamada para detener el nodo leader
    response = requests.post("http://127.0.0.1:8008/leader/stop")
    assert (
        response.status_code == 200
    ), "Fallo: Código de estado incorrecto para leader_stop"
    assert response.json().get("status") == "OK", "Fallo: No se pudo detener el leader"

    log.info("Test leader_run_and_stop pasado correctamente.")


if __name__ == "__main__":
    # *test_global_ping()
    # *test_follower_register()
    # *test_leader_register()
    # *test_scrap_result_handling()
    # *test_follower_scrap()
    # TODO test_leader_run_and_stop() Aqui como se marca cuando uno es lider?
    log.info("Todos los tests han pasado correctamente.")
