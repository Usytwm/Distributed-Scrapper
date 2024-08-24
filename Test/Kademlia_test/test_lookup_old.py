import logging
import os
import random
import sys

import sys
from pathlib import Path

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))

from src.utils.utils import N_OF_BITS, digest_to_int

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))

logging.basicConfig(level=logging.DEBUG)
from src.kademlia_network.node import Node, NodeData, distance_to


import asyncio
from src.kademlia_network.node import Node
from src.kademlia_network.node_data import NodeData

import threading
import random

log = logging.getLogger(__name__)


def test_call_ping():
    node1 = Node(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = Node(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    node3 = Node(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node3.listen()

    result = node2.call_ping(node1.node_data)
    result1 = node1.call_ping(node2.node_data)
    result2 = node2.call_ping(node1.node_data)

    assert result, f"El nodo {node2.id} no oobtuvo respuesta al ping hacia {node1.id}"

    assert result1, f"El nodo {node1.id} no oobtuvo respuesta al ping hacia {node2.id}"

    assert result2, f"El nodo {node2.id} no oobtuvo respuesta al ping hacia {node1.id}"

    log.info("Test ping sucess")


def test_call_store():
    node1 = Node(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = Node(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    key = "test_key"
    value = "test_value"

    result = node1.call_store(node2.node_data, key, value)

    assert (
        result
    ), f"El nodo {node1.id} no pudo almacenar la clave '{key}' en el nodo {node2.id}"

    # Verificar que el valor se almacenó en node2
    stored_value = node2.storage.get(key)
    assert (
        stored_value == value
    ), f"El valor almacenado en el nodo {node2.id} no coincide con el esperado"

    log.info("Test call_store passed")


def test_call_find_value():
    node1 = Node(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = Node(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    # Almacenar un valor en node2
    key = digest_to_int("test_key", num_bits=N_OF_BITS)
    value = "test_value"
    node2.storage[key] = value

    # Intentar recuperar el valor desde node1
    retrieved_value, is_value = node1.call_find_value(node2.node_data, key)

    assert (
        is_value
    ), f"El nodo {node1.id} no pudo recuperar la clave '{key}' desde el nodo {node2.id}"
    assert (
        retrieved_value == value
    ), f"El valor recuperado '{retrieved_value}' no coincide con el valor esperado '{value}'"

    log.info("Test call_find_value passed")


def test_call_find_node():
    node1 = Node(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = Node(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    node3 = Node(node_id=3, ip="127.0.0.1", port=8003, ksize=2)
    node3.listen()

    # Agregar los nodos directamente a la tabla de enrutamiento de node1
    node1.router.add(node2.node_data)
    node1.router.add(node3.node_data)

    # También puedes agregar los nodos a las tablas de enrutamiento de node2 y node3
    node2.router.add(node1.node_data)
    node2.router.add(node3.node_data)

    node3.router.add(node1.node_data)
    node3.router.add(node2.node_data)

    # Intentar encontrar los nodos más cercanos al ID de node3 desde node1
    closest_nodes = node1.call_find_node(node2.node_data, node3.id)

    assert (
        len(closest_nodes) > 0
    ), f"El nodo {node1.id} no pudo encontrar nodos cercanos al ID {node3.id}"
    assert (
        node3.node_data in closest_nodes
    ), f"El nodo {node3.id} no fue encontrado como el más cercano"

    log.info("Test call_find_node passed")


def test_lookup():
    # Crear nodos de la red
    node1 = Node(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = Node(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    node3 = Node(node_id=3, ip="127.0.0.1", port=8003, ksize=2)
    node3.listen()

    node4 = Node(node_id=4, ip="127.0.0.1", port=8004, ksize=2)
    node4.listen()

    node5 = Node(node_id=5, ip="127.0.0.1", port=8005, ksize=2)
    node5.listen()

    # Agregar nodos a la tabla de enrutamiento de node1
    node1.router.add(node2.node_data)
    node1.router.add(node3.node_data)
    node1.router.add(node4.node_data)
    node1.router.add(node5.node_data)

    # Caso de prueba 1: Buscar el propio ID de node1
    result = node1.lookup(node1.id)
    assert len(result) > 0, f"El nodo {node1.id} no encontró vecinos para su propio ID."

    # Caso de prueba 2: Buscar un nodo directamente conocido
    result = node1.lookup(node2.id)
    assert (
        len(result) > 0
    ), f"El nodo {node1.id} no encontró vecinos cercanos al ID {node2.id}"
    assert (
        node2.node_data in result
    ), f"El nodo {node2.id} no fue encontrado como el más cercano al buscar su propio ID"

    # Caso de prueba 3: Buscar un nodo que no está directamente en la tabla pero está cerca
    unknown_node_id = 6  # ID que no está directamente en la tabla
    result = node1.lookup(unknown_node_id)
    assert (
        len(result) > 0
    ), f"El nodo {node1.id} no pudo encontrar vecinos cercanos al ID {unknown_node_id}"
    # Verificar que los resultados contienen nodos cercanos
    closest = min(result, key=lambda x: distance_to(x.id, unknown_node_id))
    assert closest.id in [
        node2.id,
        node3.id,
        node4.id,
        node5.id,
    ], f"El nodo más cercano al ID {unknown_node_id} no fue correcto"

    # Caso de prueba 4: Buscar un nodo con un ID alto no directamente conocido
    high_node_id = 50  # Un ID arbitrariamente alto que no está en la tabla
    result = node1.lookup(high_node_id)
    assert (
        len(result) > 0
    ), f"El nodo {node1.id} no pudo encontrar vecinos cercanos al ID {high_node_id}"
    # Verificar que los resultados contienen nodos más cercanos al ID alto
    closest = min(result, key=lambda x: distance_to(x.id, high_node_id))
    assert closest.id in [
        node2.id,
        node3.id,
        node4.id,
        node5.id,
    ], f"El nodo más cercano al ID {high_node_id} no fue correcto"

    # Caso de prueba 5: Buscar un nodo en un espacio de IDs densamente poblado
    node7 = Node(node_id=7, ip="127.0.0.1", port=8006, ksize=2)
    node7.listen()
    node1.router.add(node7.node_data)

    result = node1.lookup(node7.id)
    assert (
        len(result) > 0
    ), f"El nodo {node1.id} no pudo encontrar vecinos cercanos al ID {node7.id}"
    assert (
        node5.node_data in result
    ), f"El nodo {node5.id} no fue encontrado como el más cercano"

    log.info("Todos los casos de prueba para lookup pasaron correctamente.")


def test_bootstrap():
    # Crear nodos de la red
    node1 = Node(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = Node(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    node3 = Node(node_id=3, ip="127.0.0.1", port=8003, ksize=2)
    node3.listen()

    node4 = Node(node_id=4, ip="127.0.0.1", port=8004, ksize=2)
    node4.listen()

    node5 = Node(node_id=5, ip="127.0.0.1", port=8005, ksize=2)
    node5.listen()

    # Agregar nodos iniciales a node1 a través del bootstrap
    bootstrap_nodes = [
        node2.node_data,
        node3.node_data,
        node4.node_data,
        node5.node_data,
    ]
    node1.bootstrap(bootstrap_nodes)

    # Caso de prueba 1: Verificar que node1 tiene nodos en su tabla de enrutamiento
    closest_nodes = node1.router.k_closest_to(node1.id)
    assert (
        len(closest_nodes) > 0
    ), "La tabla de enrutamiento de node1 está vacía después del bootstrap"

    # Caso de prueba 2: Verificar que node1 tiene los nodos más cercanos en su tabla de enrutamiento
    for node in [node3, node2]:
        assert (
            node.node_data in closest_nodes
        ), f"El nodo {node.node_data.id} no fue encontrado en la tabla de enrutamiento de node1 después del bootstrap"

    # Caso de prueba 3: Verificar que la tabla de enrutamiento de node1 se ha llenado correctamente
    expected_contacts = sorted(
        [node2.node_data, node3.node_data],
        key=lambda x: distance_to(x.id, node1.id),
    )
    actual_contacts = sorted(closest_nodes, key=lambda x: distance_to(x.id, node1.id))
    assert (
        expected_contacts == actual_contacts
    ), "Los contactos en la tabla de enrutamiento de node1 no son los más cercanos esperados"

    # Caso de prueba 4: Verificar que poblate funcionó correctamente
    # Esto debería haber intentado llenar la tabla de enrutamiento con nodos adicionales
    node_count_before = len(node1.router.get_contacts())
    node1.router.poblate()
    node_count_after = len(node1.router.get_contacts())
    assert (
        node_count_after >= node_count_before
    ), "El proceso de poblate no llenó correctamente la tabla de enrutamiento"

    # Caso de prueba 5: Verificar que el nodo sigue funcionando después de múltiples bootstrap calls
    node6 = Node(node_id=6, ip="127.0.0.1", port=8006, ksize=2)
    node6.listen()
    node1.bootstrap([node6.node_data])

    closest_nodes = node1.router.k_closest_to(node1.id)
    assert (
        node3.node_data in closest_nodes
    ), "El nodo3 no fue encontrado en la tabla de enrutamiento de node1 después de realizar bootstrap adicional"

    log.info("Todos los casos de prueba para bootstrap pasaron correctamente.")


def test_set():
    # Configuración de la red
    node1 = Node(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = Node(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    node3 = Node(node_id=3, ip="127.0.0.1", port=8003, ksize=2)
    node3.listen()

    node4 = Node(node_id=4, ip="127.0.0.1", port=8004, ksize=2)
    node4.listen()

    node1.bootstrap([node2.node_data, node3.node_data, node4.node_data])

    # Caso de prueba 1: Almacenar un valor simple
    key = "simple_key"
    value = "simple_value"
    assert node1.set(key, value), "Fallo al almacenar un valor simple en la red"

    # Verificar que el valor se almacena correctamente en los nodos más cercanos
    stored_value = node4.storage.get(digest_to_int(key, num_bits=N_OF_BITS))
    assert (
        stored_value == value
    ), f"El valor almacenado no coincide en node4: {stored_value} != {value}"

    # Caso de prueba 2: Almacenar un valor complejo
    complex_key = "complex_key_@#!$%^&*"
    complex_value = "complex_value_{}[]|\\<>"
    assert node1.set(
        complex_key, complex_value
    ), "Fallo al almacenar un valor complejo en la red"

    stored_value = node3.storage.get(digest_to_int(complex_key, num_bits=N_OF_BITS))
    assert (
        stored_value == complex_value
    ), f"El valor almacenado no coincide en node3: {stored_value} != {complex_value}"

    # Caso de prueba 3: Almacenar valores duplicados
    duplicate_key = "duplicate_key"
    value1 = "value1"
    value2 = "value2"
    assert node1.set(
        duplicate_key, value1
    ), "Fallo al almacenar el primer valor duplicado en la red"
    assert node1.set(
        duplicate_key, value2
    ), "Fallo al almacenar el segundo valor duplicado en la red"

    stored_value = node4.storage.get(digest_to_int(duplicate_key, num_bits=N_OF_BITS))
    assert (
        stored_value == value2
    ), f"El valor almacenado no coincide en node4: {stored_value} != {value2}"

    # Caso de prueba 4: Almacenar un valor cuando un nodo falla
    node4.listen = lambda: None  # Simular un fallo en node4
    failed_key = "failed_key"
    failed_value = "failed_value"
    assert node1.set(
        failed_key, failed_value
    ), "Fallo al almacenar un valor cuando un nodo falla"
    value = digest_to_int(failed_key, num_bits=N_OF_BITS)
    stored_value = node4.storage.get(value)
    assert (
        stored_value == failed_value
    ), f"El valor almacenado no coincide en node4 cuando un nodo falla: {stored_value} != {failed_value}"

    log.info("Todos los casos de prueba para set pasaron correctamente.")


def test_get():
    # Configuración de la red
    node1 = Node(node_id=1, ip="127.0.0.1", port=8001, ksize=2)
    node1.listen()

    node2 = Node(node_id=2, ip="127.0.0.1", port=8002, ksize=2)
    node2.listen()

    node3 = Node(node_id=3, ip="127.0.0.1", port=8003, ksize=2)
    node3.listen()

    node4 = Node(node_id=4, ip="127.0.0.1", port=8004, ksize=2)
    node4.listen()

    node1.bootstrap([node2.node_data, node3.node_data, node4.node_data])

    # Pre-llenar la red con algunos valores
    key = "simple_key"
    value = "simple_value"
    node1.set(key, value)

    complex_key = "complex_key_@#!$%^&*"
    complex_value = "complex_value_{}[]|\\<>"
    k = digest_to_int(complex_key, num_bits=N_OF_BITS)
    node1.set(complex_key, complex_value)

    duplicate_key = "duplicate_key"
    value1 = "value1"
    node1.set(duplicate_key, value1)

    # Caso de prueba 1: Recuperar un valor simple
    retrieved_value = node2.get(key)
    assert (
        retrieved_value == value
    ), f"El valor recuperado no coincide: {retrieved_value} != {value}"

    # Caso de prueba 2: Recuperar un valor complejo
    retrieved_value = node3.get(complex_key)
    assert (
        retrieved_value == complex_value
    ), f"El valor complejo recuperado no coincide: {retrieved_value} != {complex_value}"

    # Caso de prueba 3: Recuperar un valor duplicado
    retrieved_value = node4.get(
        duplicate_key
    )  #! Se ejecuta indefinidamente haciendo llamadas
    assert (
        retrieved_value == value1
    ), f"El valor duplicado recuperado no coincide: {retrieved_value} != {value1}"

    # Caso de prueba 4: Recuperar un valor inexistente
    non_existent_key = "non_existent_key"
    n = digest_to_int(non_existent_key, num_bits=N_OF_BITS)
    try:
        retrieved_value_non_existent_key = node1.get(non_existent_key)
        assert False, "Se esperaba una excepción para una clave inexistente"
    except Exception as e:
        log.info("Se manejó correctamente una clave inexistente.")

    # Caso de prueba 5: Recuperar un valor cuando un nodo falla
    node2.listen = lambda: None  # Simular un fallo en node2
    retrieved_value = node3.get(key)  #! Se ejecuta indefinidamente haciendo llamadas
    assert (
        retrieved_value == value
    ), f"El valor recuperado no coincide cuando un nodo falla: {retrieved_value} != {value}"

    log.info("Todos los casos de prueba para get pasaron correctamente.")


def test_bootstrapping():
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

    def bootstrap_node(node, bootstrap_nodes):
        node.bootstrap([n for n in bootstrap_nodes if n.id != node.id])

    threads = []
    for node in nodes:
        thread = threading.Thread(target=bootstrap_node, args=(node, bootstrap_nodes))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Todo Hasta aki funciono todo bien me voy a acostra que ando roto
    # Verificar que todos los nodos tienen al menos un vecino
    for node in nodes:
        closest_nodes = node.router.k_closest_to(node.id)
        assert (
            len(closest_nodes) > 0
        ), f"El nodo {node.id} no tiene vecinos cercanos después del bootstrap"

    # Test simple de set y get
    test_key = "clave_prueba"
    test_value = "valor_prueba"
    nodes[0].set(test_key, test_value)

    retrieved_value = nodes[1].get(test_key)
    assert (
        retrieved_value == test_value
    ), "El valor recuperado no coincide con el valor almacenado"

    # Test con claves y valores complejos
    complex_key = "key_with_special_chars_!@#$%^&*()"
    complex_value = "value_with_special_chars_{}[]|\\<>"
    nodes[5].set(complex_key, complex_value)

    retrieved_value = nodes[10].get(complex_key)
    assert (
        retrieved_value == complex_value
    ), "El valor complejo recuperado no coincide con el valor almacenado"

    # Simular fallo de nodo y verificar operación
    nodes[0].storage.clear()
    nodes[1].set("key_falla", "value_falla")
    retrieved_value = nodes[2].get("key_falla")
    assert (
        retrieved_value == "value_falla"
    ), "El sistema no manejó correctamente el fallo del nodo"

    # Test de alto volumen
    test_data = {f"key_{i}": f"value_{i}" for i in range(100)}

    def set_data(key, value):
        nodes[0].set(key, value)

    threads = []
    for key, value in test_data.items():
        thread = threading.Thread(target=set_data, args=(key, value))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for key, value in test_data.items():
        retrieved_value = nodes[random.randint(1, 14)].get(key)
        assert (
            retrieved_value == value
        ), f"Fallo al recuperar el valor para la clave {key}"

    print("Todos los tests pasaron correctamente.")


# Ejecutar el test
# * test_call_ping()
# * test_call_store()
# * test_call_find_value()
# * test_call_find_node()
# * test_lookup()
# * test_bootstrap()
# * test_set()
# ! test_get()
test_bootstrapping()
