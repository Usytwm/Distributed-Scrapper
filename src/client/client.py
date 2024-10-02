import argparse
from pathlib import Path
import sys
import webbrowser


path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))
from src.client.client_node import ClientNode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Iniciar un ClientNode para la red distribuida."
    )

    # Añadir argumentos para el host y puerto
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Dirección IP del cliente"
    )
    parser.add_argument("--port", type=int, default=5001, help="Puerto del cliente")

    args = parser.parse_args()

    # Crear una instancia del cliente con los parámetros del terminal
    client = ClientNode(host=args.host, port=args.port)

    # Iniciar el cliente y su servidor Flask
    client.listen()
    client.start()

    url = f"http://{args.host}:{args.port}/"
    print(f"Abriendo el navegador en {url}")
    webbrowser.open(url)
