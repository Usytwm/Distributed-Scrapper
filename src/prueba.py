import logging
import sys
from pathlib import Path
import time

import requests


path_to_root = Path(__file__).resolve().parents[1]
sys.path.append(str(path_to_root))

from src.main import load_config
from src.administration.admin_node import Admin_Node
from src.kademlia_network.kademlia_node_data import KademliaNodeData
from src.scrapper.scrapper_node import Scrapper_Node
from src.storage.storage_node import StorageNode
from src.utils.utils import NodeType

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

import subprocess
import os


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


def start_node(node_type, ip, port, bootstrap_nodes=None):
    bootstrap_nodes = bootstrap_nodes or []

    if node_type == NodeType.ADMIN:
        node = Admin_Node(ip=ip, port=port)
        node.listen()
        if bootstrap_nodes:
            # Conectar a nodos bootstrap
            node.bootstrap(bootstrap_nodes)
        else:
            # Nodo bootstrap
            node.start_leader()
        log.info(f"Levantando nodo Admin en {ip}:{port}")
        return node

    elif node_type == NodeType.SCRAPPER:
        node = Scrapper_Node(host=ip, port=port)
        node.listen()
        if bootstrap_nodes:
            node.register(bootstrap_nodes, NodeType.SCRAPPER.value)
        else:
            config = load_config()
            server_register = KademliaNodeData(
                config["bootstrap"]["admin"]["ip"],
                config["bootstrap"]["admin"]["port"],
            )
            # Si no hay nodos bootstrap, este nodo es el bootstrap inicial de la red
            node.push("entry points", server_register.to_json())
            node.register([], NodeType.SCRAPPER.value)
            log.info("No hay nodos bootstrap para Scrapper, este es el nodo bootstrap.")
        log.info(f"Levantando nodo Scrapper en {ip}:{port}")
        return node

    elif node_type == NodeType.STORAGE:
        node = StorageNode(host=ip, port=port)
        node.listen()
        if bootstrap_nodes:
            node.register(bootstrap_nodes, NodeType.STORAGE.value)
        else:
            log.info("No hay nodos bootstrap para Storage, este es el nodo bootstrap.")
            config = load_config()
            server_register = KademliaNodeData(
                config["bootstrap"]["admin"]["ip"], config["bootstrap"]["admin"]["port"]
            )
            # Si no hay nodos bootstrap, este nodo es el bootstrap inicial de la red
            node.push("entry points", server_register.to_json())
            node.register([], NodeType.STORAGE.value)
        log.info(f"Levantando nodo Storage en {ip}:{port}")
        return node


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
        10001,
        [KademliaNodeData(ip="127.0.0.1", port=10000)],
    )
    storage_node_2 = start_node(
        NodeType.STORAGE,
        "127.0.0.1",
        10002,
        [KademliaNodeData(ip="127.0.0.1", port=10000)],
    )

    data = {
        "url": "http://example.com",
    }
    response = requests.post("http://127.0.0.1:8002/push_url", json=data)

    while True:
        time.sleep(10)

    # Ahora tienes acceso a los nodos y puedes inspeccionar o interactuar con ellos.
    log.info(f"Admin Bootstrap: {admin_bootstrap}")
    log.info(f"Scrapper Bootstrap: {scrapper_bootstrap}")
    log.info(f"Storage Bootstrap: {storage_bootstrap}")

    # Puedes acceder a las propiedades de los nodos, por ejemplo:
    log.info(f"Storage Nodes: {[storage_bootstrap, storage_node_1, storage_node_2]}")
    # Aquí podrías añadir código para inspeccionar datos específicos de los nodos o realizar alguna operación.


if __name__ == "__main__":
    main()
