import logging
import requests
import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))

from src.administration.admin_node import Admin_Node
from src.kademlia_network.kademlia_node_data import KademliaNodeData
from src.scrapper.scrapper_node import Scrapper_Node
from src.storage.storage_node import StorageNode

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Inicialización de nodos de administrador
admin_nodes = []
for i in range(5):
    admin_node = Admin_Node(node_id=i, ip=f"127.0.0.1", port=8000 + i)
    admin_node.listen()
    admin_nodes.append(admin_node)

# Inicialización de nodos scrappers
scrapper_nodes = []
for i in range(5):
    scrapper_node = Scrapper_Node(host="127.0.0.1", port=8010 + i)
    scrapper_node.listen()
    scrapper_nodes.append(scrapper_node)

# Inicialización de nodos de almacenamiento
storage_nodes = []
for i in range(5):
    storage_node = StorageNode(host="127.0.0.1", port=8020 + i)
    storage_node.listen()
    storage_nodes.append(storage_node)


# Registrar nodos scrappers y almacenamiento en los administradores
def test_bootstrap_registration():
    for scrapper in scrapper_nodes:
        response = requests.post(
            "http://127.0.0.1:8000/follower/register",
            json={"role": "scrapper", "node": scrapper.node_data.to_json()},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "OK"

    for storage in storage_nodes:
        response = requests.post(
            "http://127.0.0.1:8000/follower/register",
            json={"role": "storage", "node": storage.node_data.to_json()},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "OK"

    log.info("Test de registro y bootstrap exitoso.")


def test_storage_set_get():
    test_key = "test_key"
    test_value = "test_value"

    # Almacenar un valor en el primer nodo de almacenamiento
    storage_node = storage_nodes[0]
    response = requests.post(
        f"http://127.0.0.1:{storage_node.port}/set",
        json={"key": test_key, "value": test_value},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "OK"

    # Verificar que el valor está disponible en todos los nodos de almacenamiento
    for storage in storage_nodes:
        response = requests.get(
            f"http://127.0.0.1:{storage.port}/get", json={"key": test_key}
        )
        assert response.status_code == 200
        assert response.json()["value"] == test_value

    log.info("Test de almacenamiento distribuido exitoso.")


def test_scrapper_data():
    test_url = "http://example.com"

    scrapper_node = scrapper_nodes[0]
    storage_node = storage_nodes[0]

    # Iniciar scraping y almacenar en el nodo de almacenamiento
    response = requests.post(
        f"http://127.0.0.1:{scrapper_node.port}/scrap", json={"url": test_url}
    )
    assert response.status_code == 200

    # Verificar que el contenido se almacenó en el nodo de almacenamiento
    response = requests.get(
        f"http://127.0.0.1:{storage_node.port}/get", json={"key": test_url}
    )
    assert response.status_code == 200
    assert response.json()["value"] is not None

    log.info("Test de scraping y almacenamiento exitoso.")


def test_replication_and_find_value():
    test_key = "replicated_key"
    test_value = "replicated_value"

    # Almacenar el valor en un nodo de almacenamiento
    storage_node = storage_nodes[1]
    response = requests.post(
        f"http://127.0.0.1:{storage_node.port}/set",
        json={"key": test_key, "value": test_value},
    )
    assert response.status_code == 200

    # Verificar que el valor está disponible en cualquier nodo
    for storage in storage_nodes:
        response = requests.get(
            f"http://127.0.0.1:{storage.port}/get", json={"key": test_key}
        )
        assert response.status_code == 200
        assert response.json()["value"] == test_value

    log.info("Test de replicación y búsqueda exitoso.")


def test_failure_handling():
    test_key = "failure_key"
    test_value = "failure_value"

    # Simulamos fallo en el primer nodo de almacenamiento
    failed_storage = storage_nodes[0]
    failed_storage.stop()

    # Almacenar el valor en otro nodo de almacenamiento
    storage_node = storage_nodes[1]
    response = requests.post(
        f"http://127.0.0.1:{storage_node.port}/set",
        json={"key": test_key, "value": test_value},
    )
    assert response.status_code == 200

    # Verificar que el valor se replica correctamente entre los nodos restantes
    for storage in storage_nodes[1:]:
        response = requests.get(
            f"http://127.0.0.1:{storage.port}/get", json={"key": test_key}
        )
        assert response.status_code == 200
        assert response.json()["value"] == test_value

    log.info("Test de manejo de fallos exitoso.")
