import random
import requests
import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))

from src.administration.admin_node import Admin_Node
from src.scrapper.scrapper_node import Scrapper_Node
from src.storage.storage_node import StorageNode


# Inicialización de nodos administradores, scrappers y almacenamiento
admin_nodes = []
scrapper_nodes = []
storage_nodes = []

# Creación de 5 nodos de administradores
for i in range(5):
    admin_node = Admin_Node(node_id=i, ip=f"127.0.0.1", port=8000 + i)
    admin_node.listen()
    admin_nodes.append(admin_node)

# Creación de 3 nodos scrappers
for i in range(3):
    scrapper_node = Scrapper_Node(host="127.0.0.1", port=8010 + i)
    scrapper_node.listen()
    scrapper_nodes.append(scrapper_node)

# Creación de 5 nodos de almacenamiento
for i in range(5):
    storage_node = StorageNode(host="127.0.0.1", port=8020 + i)
    storage_node.listen()
    storage_nodes.append(storage_node)


# Registro de los nodos en la red de administradores
def bootstrap_registration():
    for scrapper in scrapper_nodes:
        response = requests.post(
            "http://127.0.0.1:8000/follower/register",
            json={"role": "scrapper", "node": scrapper.node_data.to_json()},
        )
        assert response.status_code == 200

    for storage in storage_nodes:
        response = requests.post(
            "http://127.0.0.1:8000/follower/register",
            json={"role": "storage", "node": storage.node_data.to_json()},
        )
        assert response.status_code == 200

    print("Registro inicial completado.")


# Lista de URLs a scrappear
urls_to_scrap = [
    "https://www.wikipedia.org",
    "https://www.github.com",
    "https://www.python.org",
    "https://www.stackoverflow.com",
    "https://www.medium.com",
    "https://www.nytimes.com",
    "https://www.bbc.com",
    "https://www.cnn.com",
    "https://www.reuters.com",
    "https://www.theguardian.com",
    "https://www.forbes.com",
    "https://www.bloomberg.com",
    "https://www.techcrunch.com",
    "https://www.engadget.com",
    "https://www.wired.com",
    "https://www.nationalgeographic.com",
    "https://www.ted.com",
    "https://www.quora.com",
    "https://www.reddit.com",
    "https://www.linkedin.com",
]


def test_scrap_multiple_urls_with_random_scrapper():
    # Simular el envío de varias URLs, eligiendo un scrapper aleatorio
    for url in urls_to_scrap:
        # Seleccionar un scrapper aleatorio de la lista
        random_scrapper = random.choice(scrapper_nodes)

        # Enviar la URL al líder a través del scrapper elegido
        response = requests.post(
            f"http://127.0.0.1:{random_scrapper.port}/follower/scrap",
            json={
                "url": url,
                "depth": 1,
                "scrapper": random_scrapper.node_data.to_json(),
            },
        )
        assert (
            response.status_code == 200
        ), f"Fallo al scrappear {url} con el scrapper {random_scrapper.port}"

    print("Simulación de múltiples URLs con scrappers aleatorios completada.")


def test_check_pending_urls():
    # Verificamos que todavía hay URLs en espera
    response = requests.get(f"http://127.0.0.1:8000/pending_urls")
    assert response.status_code == 200
    pending_urls = response.json().get("pending_urls", [])
    assert len(pending_urls) > 0, "Deberían haber URLs pendientes"
    print("Test de URLs pendientes exitoso.")


def test_replication_and_node_joining():
    # Almacenar una URL en la red antes de que un nuevo nodo de almacenamiento se una
    test_url = "http://example.com/page8"
    test_content = "Test content"

    # Simulamos scraping de una nueva URL y almacenamos el contenido
    storage_node = storage_nodes[0]
    response = requests.post(
        f"http://127.0.0.1:{storage_node.port}/set",
        json={"key": test_url, "value": test_content},
    )
    assert response.status_code == 200

    # Agregar un nuevo nodo de almacenamiento a la red
    new_storage_node = StorageNode(host="127.0.0.1", port=8030)
    new_storage_node.listen()
    storage_nodes.append(new_storage_node)

    # El nuevo nodo debe tener acceso a los datos ya almacenados
    response = requests.get(
        f"http://127.0.0.1:{new_storage_node.port}/get", json={"key": test_url}
    )
    assert response.status_code == 200
    assert (
        response.json()["value"] == test_content
    ), "El nuevo nodo debería tener los datos replicados"

    print("Test de replicación y unión de nodo exitoso.")


def test_data_consistency_after_failure():
    test_url = "http://example.com/page9"
    test_content = "Content for testing failure"

    # Almacenar un valor en el primer nodo de almacenamiento
    storage_node = storage_nodes[0]
    response = requests.post(
        f"http://127.0.0.1:{storage_node.port}/set",
        json={"key": test_url, "value": test_content},
    )
    assert response.status_code == 200

    # Simular la caída de un nodo
    failed_node = storage_nodes[1]
    failed_node.stop()

    # Verificar que otros nodos todavía tienen acceso a los datos
    for storage in storage_nodes[2:]:
        response = requests.get(
            f"http://127.0.0.1:{storage.port}/get", json={"key": test_url}
        )
        assert response.status_code == 200
        assert (
            response.json()["value"] == test_content
        ), "Los datos no deberían perderse"

    print("Test de consistencia de datos después de fallos exitoso.")
