import logging
import os
import sys

import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))

from src.utils.utils import digest_to_int

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))

logging.basicConfig(level=logging.DEBUG)
import asyncio
from src.kademlia_network.node import Node, NodeData
import asyncio


async def run_manual_routing():
    # Crear el primer nodo
    node0 = Node(node_id=0, ip="localhost", port=7999)
    node0.listen()
    logging.info("Node 1 is running")

    # Crear el primer nodo
    node1 = Node(node_id=1, ip="localhost", port=8000)
    node1.listen()
    logging.info("Node 1 is running")

    # Crear el segundo nodo
    node2 = Node(node_id=2, ip="localhost", port=8001)
    node2.listen()
    logging.info("Node 2 is running")

    # Crear el tercer nodo
    node3 = Node(node_id=3, ip="localhost", port=8002)
    node3.listen()
    logging.info("Node 3 is running")
    # Crear el tercer nodo
    node4 = Node(node_id=4, ip="localhost", port=8003)
    node4.listen()
    logging.info("Node 3 is running")
    # Crear el tercer nodo
    node5 = Node(node_id=5, ip="localhost", port=8004)
    node5.listen()
    logging.info("Node 3 is running")
    # Crear el tercer nodo
    node6 = Node(node_id=6, ip="localhost", port=8005)
    node6.listen()
    logging.info("Node 3 is running")
    # Crear el tercer nodo
    node7 = Node(node_id=7, ip="localhost", port=8006)
    node7.listen()
    logging.info("Node 3 is running")
    # Crear el tercer nodo
    node8 = Node(node_id=8, ip="localhost", port=8007)
    node8.listen()
    logging.info("Node 3 is running")

    node9 = Node(node_id=9, ip="localhost", port=8008)
    node9.listen()
    logging.info("Node 3 is running")
    # Crear el tercer nodo
    node10 = Node(node_id=10, ip="localhost", port=8010)
    node10.listen()
    logging.info("Node 3 is running")

    # nodes = [node1, node2, node3, node3, node5, node6, node7, node8, node9, node10]

    # def test_2(routing_table, lots_of_nodes):
    #     for node in lots_of_nodes:
    #         routing_table.add(node)
    #     k_closest = routing_table.k_closest_to(8)
    #     for contact in k_closest:
    #         print(contact.id)

    # test_correct_splitting(routing_table, lots_of_nodes)
    # test_2(node1.router, nodes)

    # Esperar un momento para asegurarse de que todos los nodos están en marcha

    # Agregar manualmente node2 y node3 a la tabla de enrutamiento de node1
    await node1.router.add(node2.node_data)
    await node1.router.add(node3.node_data)
    await node1.router.add(node4.node_data)
    await node1.router.add(node5.node_data)
    await node1.router.add(node6.node_data)
    await node1.router.add(node7.node_data)
    await node1.router.add(node8.node_data)
    await node1.router.add(node9.node_data)
    await node3.router.add(node1.node_data)
    await node2.router.add(node1.node_data)

    print(node1.router)
    # value = await node1.call_ping(node2.node_data)
    # value2 = await node2.call_find_node(node1.node_data, node4.id)
    value3 = await node3.call_store(
        node1.node_data, digest_to_int("Ochoa", 4), "mendiata"
    )
    value4 = await node5.call_find_value(node1.node_data, digest_to_int("Ochoa", 4))
    result5 = await node3.lookup(node1.id)
    result6 = await node2.lookup(node3.id)

    result = await node1.set("hola", "que tal")

    value = await node0.call_ping(node1.node_data)

    node11 = Node(node_id=11, ip="localhost", port=8011)
    node11.listen()
    logging.info("Node 1 is running")
    await node11.bootstrap([NodeData(node1.id, node1.host, node1.port)])

    # Crear el primer nodo
    node12 = Node(node_id=12, ip="localhost", port=8012)
    node12.listen()
    logging.info("Node 1 is running")
    await node12.bootstrap([NodeData(node11.id, node0.host, node0.port)])

    # Crear el segundo nodo
    node13 = Node(node_id=13, ip="localhost", port=8013)
    node13.listen()
    logging.info("Node 2 is running")
    await node13.bootstrap([NodeData(node12.id, node11.host, node11.port)])
    # Mantener los nodos activos
    while True:
        await asyncio.sleep(1)


asyncio.run(run_manual_routing())
