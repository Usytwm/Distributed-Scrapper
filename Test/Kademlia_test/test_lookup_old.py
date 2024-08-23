import logging
import os
import sys

import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))

logging.basicConfig(level=logging.DEBUG)
import asyncio
from src.kademlia_network.node import Node, NodeData
import asyncio


async def run_manual_routing():
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

    print(node1.router)
    # value = await node1.call_ping(node2.node_data)
    # value2 = await node2.call_find_node(node1.node_data, node4.id)
    value3 = await node3.call_store(node1.node_data, "Ochoa", "mendiata")
    value4 = await node5.call_find_value(node1.node_data, "Ochoa")

    logging.info("Manually added Node 2 and Node 3 to the routing table of Node 1")

    # # Ahora, podemos intentar realizar algunas operaciones, como `set` y `get`
    # await node1.set("key1", "value1")
    # logging.info("Value 'value1' stored under key 'key1' by Node 1")

    # # Buscar el valor a través de node2
    # value = await node2.get("key1")
    # logging.info(f"Value retrieved by Node 2: {value}")

    # Ejecutar un lookup en Node 3 para buscar Node 1 ID
    result = await node3.lookup(node1.id)
    logging.info(f"Lookup result on Node 3 for Node 1 ID: {result}")

    # Mantener los nodos activos
    while True:
        await asyncio.sleep(1)


asyncio.run(run_manual_routing())


# async def run_nodes():
#     # Crear y ejecutar el primer nodo
#     node1 = Node(node_id=1, ip="localhost", port=8000)
#     await node1.listen(9000)
#     logging.info("Node 1 is running")

#     # Crear y ejecutar el segundo nodo
#     node2 = Node(node_id=2, ip="localhost", port=8001)
#     await node2.listen(9001)
#     logging.info("Node 2 is running")

#     # Hacer bootstrap del segundo nodo con el primero
#     await node2.bootstrap([("localhost", 9000)])
#     logging.info("Node 2 bootstrapped with Node 1")

#     # Correr indefinidamente para que los nodos permanezcan activos
#     while True:
#         await asyncio.sleep(1)


# asyncio.run(run_nodes())


# async def run_nodes_with_store_and_get():
#     # Crear y ejecutar el primer nodo
#     node1 = Node(node_id=1, ip="localhost", port=8000)
#     await node1.listen(8000)
#     logging.info("Node 1 is running")

#     # Crear y ejecutar el segundo nodo
#     node2 = Node(node_id=2, ip="localhost", port=8001)
#     await node2.listen(8001)
#     logging.info("Node 2 is running")

#     # Hacer bootstrap del segundo nodo con el primero
#     await node2.bootstrap([("localhost", 8000)])
#     logging.info("Node 2 bootstrapped with Node 1")

#     # Almacenar un valor en la red a través de node1
#     await node1.set("key1", "value1")
#     logging.info("Value 'value1' stored under key 'key1' by Node 1")

#     # Buscar el valor a través de node2
#     value = await node2.get("key1")
#     logging.info(f"Value retrieved by Node 2: {value}")

#     # Correr indefinidamente para que los nodos permanezcan activos
#     while True:
#         await asyncio.sleep(1)


# asyncio.run(run_nodes_with_store_and_get())


# async def run_nodes_with_lookup():
#     # Crear y ejecutar el primer nodo
#     node1 = Node(node_id=1, ip="localhost", port=8000)
#     await node1.listen(8000)
#     logging.info("Node 1 is running")

#     # Crear y ejecutar el segundo nodo
#     node2 = Node(node_id=2, ip="localhost", port=8001)
#     await node2.listen(8001)
#     logging.info("Node 2 is running")

#     # Hacer bootstrap del segundo nodo con el primero
#     await node2.bootstrap([("localhost", 8000)])
#     logging.info("Node 2 bootstrapped with Node 1")

#     # Almacenar un valor en la red a través de node1
#     await node1.set("key1", "value1")
#     logging.info("Value 'value1' stored under key 'key1' by Node 1")

#     # Ejecutar un lookup en Node 2 para buscar 'key1'
#     node_data = NodeData(ip="localhost", port=8000, id=1)
#     result = await node2.lookup(node_data.id)
#     logging.info(f"Lookup result on Node 2 for Node 1 ID: {result}")

#     # Correr indefinidamente para que los nodos permanezcan activos
#     while True:
#         await asyncio.sleep(1)


# asyncio.run(run_nodes_with_lookup())
