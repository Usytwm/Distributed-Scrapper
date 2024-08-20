import asyncio
import logging

from node_data import NodeData
from routing import RoutingTable
from src.Interfaces.IStorage import IStorage
from src.Interfaces.ConectionHandler import ConnectionHandler
from src.kademlia_network.storage import Storage
from utils.utils import digest

log = logging.getLogger(__name__)

class Node(ConnectionHandler):
    def __init__(self, owner_node: NodeData, storage: IStorage, ksize: int = 20):
        self.router = RoutingTable(self, ksize, owner_node)
        self.storage = storage or Storage()
        self.owner_node = owner_node

    def exposed_ping(self, nodeid):
        """Maneja una solicitud PING y devuelve el ID del nodo fuente"""
        node = NodeData(nodeid)
        self.welcome_if_new(node)
        return self.owner_node.id

    def exposed_store(self, nodeid, key, value):
        """Maneja una solicitud STORE y almacena el valor"""
        node = NodeData(nodeid)
        self.welcome_if_new(node)
        log.debug(
            "got a store request from node %s, storing '%s'='%s'", nodeid, key, value
        )
        self.storage[key] = value
        return True

    def exposed_find_node(self, nodeid, key):
        """Maneja una solicitud FIND_NODE y devuelve los vecinos más cercanos"""
        log.info("finding neighbors of %i in local table", int(nodeid.hex(), 16))
        node = NodeData(key)
        self.welcome_if_new(node)
        neighbors = self.router.find_neighbors(node)
        return list(map(tuple, neighbors))

    def exposed_find_value(self, nodeid, key):
        """Maneja una solicitud FIND_VALUE y devuelve el valor si está almacenado"""
        value = self.storage.get(key, None)
        if value is None:
            return self.exposed_find_node(nodeid, key)
        node = NodeData(key)
        self.welcome_if_new(node)
        return {"value": value}

    def welcome_if_new(self, node: NodeData):
        """Añade un nodo a la tabla de enrutamiento si es nuevo"""
        if not self.router.is_new_node(node):
            return

        log.info("never seen %s before, adding to router", node)
        for key, value in self.storage:
            keynode = NodeData(digest(key))
            neighbors = self.router.find_neighbors(keynode)
            if neighbors:
                last = neighbors[-1].distance_to(keynode)
                new_node_close = node.distance_to(keynode) < last
                first = neighbors[0].distance_to(keynode)
                this_closest = self.owner_node.distance_to(keynode) < first
            if not neighbors or (new_node_close and this_closest):
                asyncio.create_task(self.call_store(node, key, value))
        self.router.add_contact(node)

    async def call_find_node(self, node_to_ask: NodeData, node_to_find: NodeData):
        """Llama a FIND_NODE en otro nodo"""
        address = (node_to_ask.ip, node_to_ask.port)
        result = await asyncio.to_thread(
            self._find_node, address, self.owner_node.id, node_to_find.id
        )
        return self.handle_call_response(result, node_to_ask)

    async def call_find_value(self, node_to_ask: NodeData, node_to_find: NodeData):
        """Llama a FIND_VALUE en otro nodo"""
        address = (node_to_ask.ip, node_to_ask.port)
        result = await asyncio.to_thread(
            self._find_value, address, self.owner_node.id, node_to_find.id
        )
        return self.handle_call_response(result, node_to_ask)

    async def call_ping(self, node_to_ask: NodeData):
        """Llama a PING en otro nodo"""
        address = (node_to_ask.ip, node_to_ask.port)
        result = await asyncio.to_thread(self._ping, address, self.owner_node.id)
        return self.handle_call_response(result, node_to_ask)

    async def call_store(self, node_to_ask: NodeData, key, value):
        """Llama a STORE en otro nodo"""
        address = (node_to_ask.ip, node_to_ask.port)
        result = await asyncio.to_thread(
            self._store, address, self.owner_node.id, key, value
        )
        return self.handle_call_response(result, node_to_ask)

    def handle_call_response(self, result, node: NodeData):
        """Maneja la respuesta de una llamada RPC"""
        if not result[0]:
            log.warning("no response from %s, removing from router", node)
            # self.router.remove_contact(node)
            return result

        log.info("got successful response from %s", node)
        self.welcome_if_new(node)
        return result
