import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))


import logging

from src.kademlia_network.kademlia_node import KademliaNode
from src.utils.utils import N_OF_BITS, digest_to_int


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_kademlia_queue_node():
    pass


if __name__ == "__main__":
    test_kademlia_queue_node()
