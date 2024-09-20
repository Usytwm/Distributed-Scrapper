import argparse
import json
import logging
import sys
from pathlib import Path


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
    match node_type:
        case NodeType.ADMIN:
            node = Admin_Node(ip=args.ip, port=args.port)
            node.listen()
            if bootstrap_nodes and len(bootstrap_nodes) > 0:
                # Si hay nodos bootstrap, conectarse a ellos
                node.bootstrap(bootstrap_nodes)
            else:
                # Si no hay nodos bootstrap, este nodo es el bootstrap inicial de la red
                node.leader_run()
            log.info(f"Levantando nodo Admin en {args.ip}:{args.port}")
        case NodeType.SCRAPPER:
            node = Scrapper_Node(host=args.ip, port=args.port)
            node.listen()
            if bootstrap_nodes and len(bootstrap_nodes) > 0:
                # Registrar el nodo en los nodos bootstrap
                node.register(bootstrap_nodes, NodeType.SCRAPPER.value)
            else:
                config = load_config()
                server_register = KademliaNodeData.from_json(
                    config["bootstrap"]["admin"]
                )
                log.info(f"Server register: {server_register}")
                # Si no hay nodos bootstrap, este nodo es el bootstrap inicial de la red
                node.push("entry points", server_register.to_json())
                node.register([], NodeType.SCRAPPER.value)

            log.info(f"Levantando nodo Scrapper en {args.ip}:{args.port}")
        case NodeType.STORAGE:
            node = StorageNode(host=args.ip, port=args.port)
            node.listen()
            if bootstrap_nodes and len(bootstrap_nodes) > 0:
                # Registrar el nodo en los nodos bootstrap
                node.register(bootstrap_nodes, NodeType.STORAGE.value)
            else:
                config = load_config()
                server_register = KademliaNodeData.from_json(
                    config["bootstrap"]["admin"]
                )
                # Si no hay nodos bootstrap, este nodo es el bootstrap inicial de la red
                node.push("entry points", server_register.to_json())
                node.register([], NodeType.STORAGE.value)
            log.info(f"Levantando nodo Storage en {args.ip}:{args.port}")


if __name__ == "__main__":
    main()
