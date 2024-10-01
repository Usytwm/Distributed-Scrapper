import logging
import sys
from pathlib import Path
import time
import requests
import subprocess
import os


path_to_root = Path(__file__).resolve().parents[1]
sys.path.append(str(path_to_root))

from src.main import load_config, start_node
from src.administration.admin_node import Admin_Node
from src.kademlia_network.kademlia_node_data import KademliaNodeData
from src.scrapper.scrapper_node import Scrapper_Node
from src.storage.storage_node import StorageNode
from src.utils.utils import NodeType

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def kill_processes_on_port(port):
    # Ejecutar netstat para obtener los procesos que están usando el puerto
    command = f"netstat -ano | findstr :{port}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Revisar si hay resultados (procesos en el puerto)
    if result.stdout:
        # Iterar sobre cada línea de la salida
        for line in result.stdout.strip().split("\n"):
            # Obtener el PID (última columna de la línea)
            pid = line.split()[-1]
            try:
                # Terminar el proceso con taskkill
                os.system(f"taskkill /PID {pid} /F")
                print(f"Proceso con PID {pid} fue terminado.")
            except Exception as e:
                print(f"No se pudo terminar el proceso con PID {pid}: {e}")
    else:
        print(f"No se encontraron procesos en el puerto {port}.")


def main():
    # Admin Nodes
    admin_bootstrap = start_node(
        NodeType.ADMIN, "127.0.0.1", 8000
    )  # Nodo Admin Bootstrap
    admin_node_1 = start_node(
        NodeType.ADMIN, "127.0.0.1", 8001, [KademliaNodeData(ip="127.0.0.1", port=8000)]
    )
    admin_node_2 = start_node(
        NodeType.ADMIN, "127.0.0.1", 8002, [KademliaNodeData(ip="127.0.0.1", port=8000)]
    )

    # Scrapper Nodes
    scrapper_bootstrap = start_node(
        NodeType.SCRAPPER, "127.0.0.1", 9000
    )  # Nodo Scrapper Bootstrap
    scrapper_node_1 = start_node(
        NodeType.SCRAPPER,
        "127.0.0.1",
        9001,
        [KademliaNodeData(ip="127.0.0.1", port=9000)],
    )
    scrapper_node_2 = start_node(
        NodeType.SCRAPPER,
        "127.0.0.1",
        9002,
        [KademliaNodeData(ip="127.0.0.1", port=9000)],
    )

    # Storage Nodes
    storage_bootstrap = start_node(
        NodeType.STORAGE, "127.0.0.1", 10000
    )  # Nodo Storage Bootstrap
    storage_node_1 = start_node(
        NodeType.STORAGE,
        "127.0.0.1",
        100001,
        [KademliaNodeData(ip="127.0.0.1", port=10000)],
    )
    storage_node_2 = start_node(
        NodeType.STORAGE,
        "127.0.0.1",
        10002,
        [KademliaNodeData(ip="127.0.0.1", port=10000)],
    )

    data = {
        "url": "https://example.com",
    }
    response = requests.post("http://127.0.0.1:8002/push_url", json=data)

    queries = [
        "https://example.com",
        "https://www.iana.org/domains/example",
        "https://www.iana.org/",
        "https://www.iana.org/about",
        # "https://www.iana.org/help/example-domains",
    ]
    answers = []
    while True:
        time.sleep(3)
        for url in queries[len(answers) :]:
            answer = storage_bootstrap.get(url)
            if not answer:
                break
            answers.append(answer)
        if len(answers) == len(queries):
            break

    x = storage_bootstrap.get("https://example.com")
    y = storage_node_1.get("https://www.iana.org/domains/example")
    b = storage_bootstrap.get("http://www.iana.org/help/example-domains")
    # Ahora tienes acceso a los nodos y puedes inspeccionar o interactuar con ellos.
    log.info(f"Admin Bootstrap: {admin_bootstrap}")
    log.info(f"Scrapper Bootstrap: {scrapper_bootstrap}")
    log.info(f"Storage Bootstrap: {storage_bootstrap}")

    # Puedes acceder a las propiedades de los nodos, por ejemplo:
    log.info(f"Storage Nodes: {[storage_bootstrap, storage_node_1, storage_node_2]}")
    # Aquí podrías añadir código para inspeccionar datos específicos de los nodos o realizar alguna operación.


if __name__ == "__main__":
    main()
