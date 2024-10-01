import argparse
import json
import logging
import sys
from pathlib import Path

#! cuando se une un nodos nuevo, verificar sui es menor que el lider, de ser asi este pasa a ser el lider y se infroma a la red

path_to_root = Path(__file__).resolve().parents[1]
sys.path.append(str(path_to_root))

from src.utils.utils import NodeType
from src.administration.admin_node import Admin_Node
from src.kademlia_network.kademlia_node_data import KademliaNodeData
from src.scrapper.scrapper_node import Scrapper_Node
from src.storage.storage_node import StorageNode

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def load_config():
    config_path = Path(__file__).resolve().parents[0] / "config.json"
    print("nsm", config_path)
    # Cargar archivo de configuración JSON con nodos bootstrap
    with open(config_path, "r") as config_file:
        return json.load(config_file)


def start_node(node_type, ip, port, bootstrap_nodes=None):
    bootstrap_nodes = bootstrap_nodes or []

    if node_type == NodeType.ADMIN:
        node = Admin_Node(ip=ip, port=port)
        node.listen()
        if bootstrap_nodes:
            # Conectar a nodos bootstrap
            node.register(bootstrap_nodes, NodeType.ADMIN.value)
            # node.bootstrap(bootstrap_nodes)
        else:
            # Nodo bootstrap
            node.start_leader()
            node.register([], NodeType.ADMIN.value)
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
                ip=config["bootstrap"]["admin"]["ip"],
                port=config["bootstrap"]["admin"]["port"],
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
                ip=config["bootstrap"]["admin"]["ip"],
                port=config["bootstrap"]["admin"]["port"],
            )
            # Si no hay nodos bootstrap, este nodo es el bootstrap inicial de la red
            node.push("entry points", server_register.to_json())
            node.register([], NodeType.STORAGE.value)
        log.info(f"Levantando nodo Storage en {ip}:{port}")
        return node


def main():
    # Configurar argparse para recibir los parámetros por consola
    parser = argparse.ArgumentParser(description="Levanta un nodo en la red")

    parser.add_argument(
        "--type",
        choices=[role.value for role in NodeType],
        required=True,
        help="Tipo de nodo a levantar: admin, scrapper o storage",
    )
    parser.add_argument(
        "-i",
        "--ip",
        type=str,
        default="127.0.0.1",
        required=True,
        help="Dirección IP del nodo",
    )
    parser.add_argument("-p", "--port", type=int, required=True, help="Puerto del nodo")
    parser.add_argument(
        "-b",
        "--bootstrap",
        help="Nodos para hacer bootstrap en formato ip:port",
        nargs="+",
    )

    # Parsear los argumentos de la línea de comandos
    args = parser.parse_args()
    node_type = NodeType(args.type)

    bootstrap_nodes = []

    if args.bootstrap:
        # Parsear los nodos bootstrap
        for node in args.bootstrap:
            ip, port = node.split(":")
            bootstrap_nodes.append(KademliaNodeData(ip=ip, port=int(port)))

    # Levantar el nodo según el tipo seleccionado
    node = start_node(node_type, args.ip, args.port, bootstrap_nodes)


if __name__ == "__main__":
    main()
