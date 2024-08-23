import pytest
import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))
from src.kademlia_network.Kdemlia_Node import Node
from src.kademlia_network.routing_table import Routing_Table
from src.kademlia_network.node_data import NodeData
from src.kademlia_network.kBucket import KBucket


@pytest.fixture
def node():
    return Node(node_id=1)


@pytest.fixture
def routing_table(node):
    return Routing_Table(owner_node=node, bucket_max_size=2)


@pytest.fixture
def lots_of_nodes():
    return [
        NodeData(id=2),
        NodeData(id=3),
        NodeData(id=7),
        NodeData(id=4),
        NodeData(id=11),
        NodeData(id=5),
        NodeData(id=6),
        NodeData(id=14),
        NodeData(id=9),
        NodeData(id=10),
    ]


def print_KBucket(kbucket: KBucket):
    print("Kbucket: " + str((kbucket.start, kbucket.end)))
    for contact in kbucket.get_contacts():
        print(contact)
    print("--------------------------------------------------")


def print_routing_table(rt: Routing_Table):
    for start, kbucket in rt.buckets.items():
        print_KBucket(kbucket)
    print("__________________________________________________")
    print("__________________________________________________")


"""
def test_add_node(routing_table, node):
    node_to_add = Node(node_id=7)
    routing_table.add(node_to_add)
    assert node_to_add.id in routing_table


def test_remove_node(routing_table, node):
    node_to_remove = Node(node_id=8)
    routing_table.add(node_to_remove)
    routing_table.remove(node_to_remove.id)
    assert node_to_remove.id not in routing_table
"""


def test_correct_splitting(routing_table, lots_of_nodes):
    for node in lots_of_nodes:
        routing_table.add(node)
        print_routing_table(routing_table)
        input()
    assert True
