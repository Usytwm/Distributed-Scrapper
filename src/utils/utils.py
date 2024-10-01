from enum import Enum
import hashlib
import operator
import asyncio

from flask import json


class NodeType(Enum):
    ADMIN = "admin"
    SCRAPPER = "scrapper"
    STORAGE = "storage"


N_OF_BITS = 160


def generate_id(ip, port):
    # Combinar la IP y el puerto en un solo string
    ip_port_string = f"{ip}:{port}"

    # Generar un hash SHA-256 de la combinación IP:puerto
    hash_value = hashlib.sha256(ip_port_string.encode()).hexdigest()

    # Convertir el hash a un entero
    hash_int = int(hash_value, 16)

    # Asegurarse de que el valor está dentro del rango permitido (0 a (1 << N_OF_BITS) - 1)
    return hash_int % (1 << N_OF_BITS)


async def gather_dict(dic):
    # Recopila los resultados de un diccionario de corutinas
    cors = list(dic.values())
    results = await asyncio.gather(*cors)
    return dict(zip(dic.keys(), results))


def digest(string):
    # Calcula el hash SHA-1 de una cadena y devuelve su digest
    if not isinstance(string, bytes):
        string = str(string).encode("utf8")
    return hashlib.sha1(string).digest()


def digest_to_int(string, num_bits=160):
    # Calcula el hash SHA-1 de una cadena y devuelve su digest truncado a `num_bits` bits
    full_digest = digest(string)

    # Convertir los bytes truncados en un número entero
    return int.from_bytes(full_digest, byteorder="big") % (1 << num_bits)


def shared_prefix(args):
    # Encuentra el prefijo compartido más largo entre varias cadenas
    i = 0
    while i < min(map(len, args)):
        if len(set(map(operator.itemgetter(i), args))) != 1:
            break
        i += 1
    return args[0][:i]


def bytes_to_bit_string(bites):
    # Convierte una secuencia de bytes en una cadena de bits
    bits = [bin(bite)[2:].rjust(8, "0") for bite in bites]
    return "".join(bits)


def get_nodes_bootstrap(role: NodeType):
    with open("../config.json", "r") as f:
        data = json.load(f)

    match role:
        case NodeType.ADMIN:
            nodes = data["bootstrap"]["admin"]
        case NodeType.SCRAPPER:
            nodes = data["bootstrap"]["scrapper"]
        case NodeType.STORAGE:
            nodes = data["bootstrap"]["storage"]
        case _:
            nodes = data["bootstrap"]["admin"]

    return nodes


def get_nodes(role: NodeType):
    with open("../config.json", "r") as f:
        data = json.load(f)

    match role:
        case NodeType.ADMIN:
            nodes = data["nodes"]["admin"]
        case NodeType.SCRAPPER:
            nodes = data["nodes"]["scrapper"]
        case NodeType.STORAGE:
            nodes = data["nodes"]["storage"]
        case _:
            nodes = data["nodes"]["admin"]

    return nodes


def hardcode_urls(
    admin_node,
    urls,
):
    """
    Función para hardcodear una serie de URLs en la red a través de un nodo Admin.

    :param admin_node: Instancia del nodo Admin_Node.
    :param urls: Lista de URLs a agregar a la red.
    """
    for url in urls:
        admin_node.push("urls", (url, admin_node.max_depth))
        print(f"URL {url} añadida a la red con profundidad {admin_node.max_depth}")


# # Ejemplo de URLs hardcodeadas
# urls_to_scrap = [
#     "https://www.example.com",
#     "https://www.wikipedia.org",
#     "https://www.python.org",
#     "https://www.github.com",
#     "https://www.stackoverflow.com",
#     "https://www.reddit.com",
#     "https://www.medium.com",
#     "https://www.nytimes.com",
#     "https://www.bbc.com",
#     "https://www.cnn.com"
# ]
