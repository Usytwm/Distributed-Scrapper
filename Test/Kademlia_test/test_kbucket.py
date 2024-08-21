import pytest
from src.kademlia_network.node_data import NodeData
from src.kademlia_network.kBucket import KBucket


@pytest.fixture
def node_data():
    return NodeData(id=123456789)


@pytest.fixture
def kbucket(node_data):
    return KBucket(owner_node=node_data, bucket_max_size=5, start=0, end=100)


def test_add_new_node(kbucket, node_data):
    # Asumiendo que existe una función 'add' que añade un nodo
    result = kbucket.add(node_data)
    assert result == True
    assert node_data.id in kbucket.contacts


def test_split_kbucket(kbucket):
    # Asumiendo que el KBucket puede ser dividido
    left, right = kbucket.split()
    assert left.end == 50
    assert right.start == 51
