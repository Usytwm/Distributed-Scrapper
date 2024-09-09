import argparse
import json
import logging
import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[1]
sys.path.append(str(path_to_root))
from src.administration.admin_node import Admin_Node
from src.kademlia_network.kademlia_node_data import KademliaNodeData
from src.scrapper.scrapper_node import Scrapper_Node
from src.storage.storage_node import StorageNode

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def load_config():
    # Cargar archivo de configuración JSON con nodos bootstrap
    with open("config.json", "r") as config_file:
        return json.load(config_file)


def main():
    # Configurar argparse para recibir los parámetros por consola
    parser = argparse.ArgumentParser(description="Levanta un nodo en la red")

    parser.add_argument(
        "--type",
        choices=["admin", "scrapper", "storage"],
        required=True,
        help="Tipo de nodo a levantar: admin, scrapper o storage",
    )
    parser.add_argument("--ip", required=True, help="Dirección IP del nodo")
    parser.add_argument("--port", type=int, required=True, help="Puerto del nodo")

    # Parsear los argumentos de la línea de comandos
    args = parser.parse_args()

    # Cargar configuración
    config = load_config()

    # Obtener el nodo bootstrap correcto según el tipo de nodo
    if args.type == "admin":
        bootstrap_node = KademliaNodeData(
            ip=config["bootstrap"]["admin"]["ip"],
            port=config["bootstrap"]["admin"]["port"],
        )
        node = Admin_Node(ip=args.ip, port=args.port)
        node.listen()
        node.bootstrap([bootstrap_node])
        log.info(f"Levantando nodo Admin en {args.ip}:{args.port}")

    elif args.type == "scrapper":
        bootstrap_node = KademliaNodeData(
            ip=config["bootstrap"]["scrapper"]["ip"],
            port=config["bootstrap"]["scrapper"]["port"],
        )
        node = Scrapper_Node(host=args.ip, port=args.port)
        node.listen()
        node.register(bootstrap_node)
        log.info(f"Levantando nodo Scrapper en {args.ip}:{args.port}")

    elif args.type == "storage":
        bootstrap_node = KademliaNodeData(
            ip=config["bootstrap"]["storage"]["ip"],
            port=config["bootstrap"]["storage"]["port"],
        )
        node = StorageNode(host=args.ip, port=args.port)
        node.listen()
        node.register(bootstrap_node)
        log.info(f"Levantando nodo Storage en {args.ip}:{args.port}")


if __name__ == "__main__":
    main()
