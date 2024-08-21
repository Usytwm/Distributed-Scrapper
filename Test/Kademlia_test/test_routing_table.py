import pytest
from src.kademlia_network.Kdemlia_Node import Node
from src.kademlia_network.routing_table import Routing_Table
from src.kademlia_network.node_data import NodeData


@pytest.fixture
def node():
    return Node(node_id=987654321)


@pytest.fixture
def routing_table(node):
    return Routing_Table(owner_node=node, bucket_max_size=10)


def test_add_node(routing_table, node):
    node_to_add = Node(node_id=12345)
    routing_table.add(node_to_add)
    assert node_to_add in routing_table


def test_remove_node(routing_table, node):
    node_to_remove = Node(node_id=12345)
    routing_table.add(node_to_remove)
    routing_table.remove(node_to_remove)
    assert node_to_remove not in routing_table
