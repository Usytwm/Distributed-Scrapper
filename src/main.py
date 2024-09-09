import argparse
import json
from src.administration.admin_node import Admin_Node
from src.kademlia_network.kademlia_node_data import KademliaNodeData
from src.scrapper.scrapper_node import Scrapper_Node
from src.storage.storage_node import StorageNode

# Tu clase de nodo Storage


def load_config():
    # Cargar archivo de configuración JSON
    with open("config.json", "r") as config_file:
        return json.load(config_file)


def main():
    # Configurar argparse para leer argumentos de la consola
    parser = argparse.ArgumentParser(description="Levanta un nodo en la red Kademlia")
    parser.add_argument(
        "--type",
        choices=["admin", "scrapper", "storage"],
        required=True,
        help="Tipo de nodo a levantar",
    )
    parser.add_argument("--ip", required=True, help="Dirección IP del nodo")
    parser.add_argument("--port", type=int, required=True, help="Puerto del nodo")

    # Parsear los argumentos
    args = parser.parse_args()

    # Cargar configuración
    config = load_config()

    # Según el tipo de nodo, levantar el nodo correcto
    if args.type == "admin":
        # Obtener el nodo bootstrap de admin
        bootstrap_data = config["bootstrap"]["admin"]
        bootstrap_node = KademliaNodeData(
            ip=bootstrap_data["ip"], port=bootstrap_data["port"]
        )
        node = Admin_Node(ip=args.ip, port=args.port)
        print(f"Levantando nodo Admin en {args.ip}:{args.port}")

    elif args.type == "scrapper":
        # Obtener el nodo bootstrap de scrappers
        bootstrap_data = config["bootstrap"]["scrapper"]
        bootstrap_node = KademliaNodeData(
            ip=bootstrap_data["ip"], port=bootstrap_data["port"]
        )
        node = Scrapper_Node(host=args.ip, port=args.port)
        print(f"Levantando nodo Scrapper en {args.ip}:{args.port}")

    elif args.type == "storage":
        # Obtener el nodo bootstrap de storage
        bootstrap_data = config["bootstrap"]["storage"]
        bootstrap_node = KademliaNodeData(
            ip=bootstrap_data["ip"], port=bootstrap_data["port"]
        )
        node = StorageNode(host=args.ip, port=args.port)
        print(f"Levantando nodo Storage en {args.ip}:{args.port}")

    # Bootstrap para unirse a la red
    node.bootstrap([bootstrap_node])
    node.listen()  # Iniciar el servidor Flask para este nodo


if __name__ == "__main__":
    main()
