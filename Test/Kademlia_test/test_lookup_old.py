import logging
import os
import random
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


import asyncio
from src.kademlia_network.node import Node
from src.kademlia_network.node_data import NodeData


async def test_bootstrapping():
    # Número de nodos en la red
    num_nodes = 15
    ksize = 2
    nodes = []

    # Creación de nodos
    for i in range(num_nodes):
        node = Node(node_id=i, ip="127.0.0.1", port=60000 + i, ksize=ksize)
        node.listen()
        nodes.append(node)

    # Bootstrap de la red
    bootstrap_nodes = [
        NodeData(ip=node.host, port=node.port, id=node.id) for node in nodes
    ]
    await asyncio.gather(
        *[
            node.bootstrap([n for n in bootstrap_nodes if n.id != node.id])
            for node in nodes
        ]
    )

    # Verificar que todos los nodos tienen al menos un vecino
    for node in nodes:
        closest_nodes = node.router.k_closest_to(node.id)
        assert (
            len(closest_nodes) > 0
        ), f"El nodo {node.id} no tiene vecinos cercanos después del bootstrap"

    # Test simple de set y get
    test_key = "clave_prueba"
    test_value = "valor_prueba"
    await nodes[0].set(test_key, test_value)

    retrieved_value = await nodes[1].get(test_key)
    assert (
        retrieved_value == test_value
    ), "El valor recuperado no coincide con el valor almacenado"

    # Test con claves y valores complejos
    complex_key = "key_with_special_chars_!@#$%^&*()"
    complex_value = "value_with_special_chars_{}[]|\\<>"
    await nodes[5].set(complex_key, complex_value)

    retrieved_value = await nodes[10].get(complex_key)
    assert (
        retrieved_value == complex_value
    ), "El valor complejo recuperado no coincide con el valor almacenado"

    # Simular fallo de nodo y verificar operación
    nodes[0].storage.clear()
    await nodes[1].set("key_falla", "value_falla")
    retrieved_value = await nodes[2].get("key_falla")
    assert (
        retrieved_value == "value_falla"
    ), "El sistema no manejó correctamente el fallo del nodo"

    # Test de alto volumen
    test_data = {f"key_{i}": f"value_{i}" for i in range(100)}
    await asyncio.gather(
        *[nodes[0].set(key, value) for key, value in test_data.items()]
    )

    for key, value in test_data.items():
        retrieved_value = await nodes[random.randint(1, 19)].get(key)
        assert (
            retrieved_value == value
        ), f"Fallo al recuperar el valor para la clave {key}"

    print("Todos los tests pasaron correctamente.")


# Ejecutar el test
asyncio.run(test_bootstrapping())


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
