import sys
import asyncio
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))
from src.kademlia_network.node import Node


def test_node():
    node_1 = Node(1, None, "localhost", 8080)
    node_2 = Node(2, None, "localhost", 8081)
    node_2.listen()
    asyncio.threads(node_1.call_ping(node_2.node_data))


test_node()
