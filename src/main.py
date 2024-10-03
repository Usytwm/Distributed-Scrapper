import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path


path_to_root = Path(__file__).resolve().parents[1]
sys.path.append(str(path_to_root))

from src.utils.utils import NodeType
from src.administration.admin_node import Admin_Node
from src.kademlia_network.kademlia_node_data import KademliaNodeData
from src.scrapper.scrapper_node import Scrapper_Node
from src.storage.storage_node import StorageNode

# Configurar el nivel de logging global a ERROR (para evitar DEBUG e INFO)
# logging.basicConfig(level=logging.DEBUG)

# Desactivar logs de urllib3
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# Desactivar logs de werkzeug (Flask)
logging.getLogger("werkzeug").setLevel(logging.CRITICAL)

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


def start_node(node_type, ip, port):
    if node_type == NodeType.ADMIN:
        node = Admin_Node(ip=ip, port=port)
    elif node_type == NodeType.SCRAPPER:
        node = Scrapper_Node(host=ip, port=port)
    elif node_type == NodeType.STORAGE:
        node = StorageNode(host=ip, port=port)

    node.listen()
    node.start()
    return node


def main():
    # Configurar argparse para recibir los parámetros por consola
    parser = argparse.ArgumentParser(description="Levanta un nodo en la red")

    parser.add_argument(
        "-t",
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
        help="Dirección IP del nodo",
    )
    parser.add_argument("-p", "--port", type=int, required=True, help="Puerto del nodo")

    # Parsear los argumentos de la línea de comandos
    args = parser.parse_args()
    node_type = NodeType(args.type)

    try:
        # Levantar el nodo según el tipo seleccionado
        node = start_node(node_type, args.ip, args.port)

    except KeyboardInterrupt:
        # Capturar Ctrl+C y manejar la salida
        log.debug("Interrupción por Ctrl+C detectada. Apagando el nodo...")
        kill_processes_on_port(args.port)
        # Aquí podrías agregar la lógica para liberar recursos si fuera necesario.
        sys.exit(0)


if __name__ == "__main__":
    main()
