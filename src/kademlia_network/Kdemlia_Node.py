import asyncio
import logging
import pickle
import random

from sortedcontainers import SortedList
from src.kademlia_network.node_data import NodeData
from src.Interfaces.IStorage import IStorage
from src.Interfaces.ConectionHandler import ConnectionHandler
from src.kademlia_network.routing_table import Routing_Table
from src.kademlia_network.storage import Storage
from src.utils.utils import digest, gather_dict
from rpyc.utils.server import ThreadedServer

log = logging.getLogger(__name__)


class Node(ConnectionHandler):
    def __init__(
        self,
        node_id,
        storage: IStorage = None,
        ip=None,
        port=None,
        ksize: int = 2,
        alpha=3,
    ):
        self.router = Routing_.Table(self, ksize)
        self.storage = storage or Storage()
        self.alpha = alpha
        self.id = node_id or digest(random.getrandbits(255))
        self.host = ip
        self.port = port
        self.ksize = ksize
        self.node_data = NodeData(ip=self.host, port=self.port, id=self.id)

    def exposed_ping(self, node: NodeData):
        """Maneja una solicitud PING y devuelve el ID del nodo fuente"""
        self.welcome_if_new(node)
        return self.id  # Por que devolvemos esto?

    def exposed_store(self, node: NodeData, key: int, value):
        """Maneja una solicitud STORE y almacena el valor"""
        self.welcome_if_new(node)
        log.debug(
            "got a store request from node %s, storing '%s'='%s'", node.id, key, value
        )
        self.storage[key] = value
        return True

    def exposed_find_node(self, node: NodeData, key):
        """Maneja una solicitud FIND_NODE y devuelve los vecinos más cercanos"""
        log.info("finding neighbors of %i in local table", key)
        self.welcome_if_new(node)
        return self.router.k_closest_to(key)

    def exposed_find_value(self, node: NodeData, key):
        """Maneja una solicitud FIND_VALUE y devuelve el valor si está almacenado"""
        value = self.storage.get(key, None)
        if value is None:
            return self.exposed_find_node(
                node, key
            )  # Porque find_node y no find_value?
        self.welcome_if_new(id)
        return {"value": value}

    def welcome_if_new(self, node: NodeData):
        """Añade un nodo a la tabla de enrutamiento si es nuevo"""
        if not node.id in self.router:
            return

        log.info("never seen %s before, adding to router", node)
        for key, value in self.storage:
            keynode_id = id = digest(key)
            neighbors = self.router.k_closest_to(keynode_id)
            if neighbors:
                last = distance_to(neighbors[-1].id, keynode_id)
                new_node_close = distance_to(node.id, keynode_id) < last
                first = distance_to(neighbors[0].id, keynode_id)
                this_closest = distance_to(self.id, keynode_id) < first
            if not neighbors or (new_node_close and this_closest):
                asyncio.create_task(self.call_store(node, key, value))
        self.router.add(node)

    async def call_find_node(self, node_to_ask: NodeData, node_to_find: NodeData):
        """Llama a FIND_NODE en otro nodo"""
        address = (node_to_ask.ip, node_to_ask.port)
        result = await asyncio.to_thread(
            self._find_node, address, self.node_data, node_to_find.id
        )
        return self.handle_call_response(result, node_to_ask)

    async def call_find_value(self, node_to_ask: NodeData, node_to_find: NodeData):
        """Llama a FIND_VALUE en otro nodo"""
        address = (node_to_ask.ip, node_to_ask.port)
        result = await asyncio.to_thread(
            self._find_value, address, self.node_data, node_to_find.id
        )
        return self.handle_call_response(result, node_to_ask)

    async def call_ping(self, node_to_ask: NodeData):
        """Llama a PING en otro nodo"""
        address = (node_to_ask.ip, node_to_ask.port)
        result = await asyncio.to_thread(self._ping, address, self.id)
        return self.handle_call_response(result, node_to_ask)

    async def call_store(self, node_to_ask: NodeData, key, value):
        """Llama a STORE en otro nodo"""
        address = (node_to_ask.ip, node_to_ask.port)
        result = await asyncio.to_thread(self._store, address, self.id, key, value)
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

    # TODO New
    async def listen(self, port, interface="0.0.0.0"):
        """Inicia el nodo en la interfaz y puerto especificados usando RPyC"""
        self.host = interface
        self.port = port
        log.info(f"Node {self.id} listening on {interface}:{port}")
        server = ThreadedServer(
            self, port=port, protocol_config={"allow_all_attrs": True}
        )
        await asyncio.to_thread(server.start)

    async def bootstrap(self, addrs):
        """Realiza el bootstrap del nodo utilizando las direcciones iniciales"""
        log.debug(f"Attempting to bootstrap node with {len(addrs)} initial contacts")
        tasks = [self.call_ping(NodeData(ip=addr[0], port=addr[1])) for addr in addrs]
        results = await asyncio.gather(*tasks)
        # eliminar cuaalquier nodo que no respondio o o se pudo conytactar haciendo ping
        nodes = [
            NodeData(addr[0], addr[1], result[1])
            for result, addr in zip(results, addrs)
            if result[0]
        ]

        # Todo guardar en la routing table los nodos que me devolvieron el ping
        # dicts = {}
        # for peer in nodes:
        #     self.router.add(peer)
        #     dicts[peer.id] = self.call_find_node(peer, self.node)
        # found = await gather_dict(dicts)
        # nearest_nodes = []

        # for _, response in found.items():
        #     response = RPCFindResponse(response)
        #     if response.happened():
        #         nearest_nodes.extend(response.get_node_list())
        # dict = {}
        # for peer in nearest_nodes:
        #     self.router.add(peer)
        #     dict[peer.id] = self.call_find_node(peer, self.node)
        # found = await gather_dict(dicts)
        # return nearest_nodes

        # Todo Impolemetar como guardar la informacion de los nodos emn la red,

    async def get(self, key):
        """Busca un valor en la red"""
        log.info(f"Looking up key {key}")
        dkey = digest(key)
        if dkey in self.storage:
            return self.storage.get(dkey)

        node = NodeData(id=dkey)
        nearest = self.router.k_closest_to(node.id)
        if not nearest:
            log.warning(f"There are no known neighbors to get key {key}")
            return None
        # LLamo a buscar el valor en los K VECINOS MAS CERCANOS MIOS
        tasks = [self.call_find_value(n, node) for n in nearest]
        results = await asyncio.gather(*tasks)
        for result in results:
            if "value" in result:
                return result["value"]
        return None

    async def set(self, key, value):
        """Almacena un valor en la red"""

        log.info(f"Setting '{key}' = '{value}' on network")
        dkey = digest(key)
        self.storage[dkey] = value

        node = NodeData(id=dkey)
        nearest = self.router.k_closest_to(node.id)
        if not nearest:
            log.warning(f"There are no known neighbors to set key {key}")
            return False
        # spider = NodeSpiderCrawl(self.protocol, node, nearest,
        #                          self.ksize, self.alpha)
        # nodes = await spider.find()
        # log.info("setting '%s' on %s", dkey.hex(), list(map(str, nodes)))

        # # if this node is close too, then store here as well
        # biggest = max([n.distance_to(node) for n in nodes])
        # if self.node.distance_to(node) < biggest:
        #     self.storage[dkey] = value
        # results = [self.protocol.call_store(n, dkey, value) for n in nodes]
        # # return true only if at least one store call succeeded
        # return any(await asyncio.gather(*results))
        # Guardio en los vecinos mas cercanos a ese key
        tasks = [self.call_store(n, dkey, value) for n in nearest]
        await asyncio.gather(*tasks)
        return True

    def bootstrappable_k_closest(self):
        neighbors = self.router.k_closest_to(self.node_data.id)
        return [tuple(n)[-2:] for n in neighbors]

    def save_state(self, fname):
        """Guarda el estado del nodo en un archivo"""
        log.info(f"Saving state to {fname}")
        data = {
            "ksize": self.ksize,
            "alpha": self.alpha,
            "id": self.id,
            "storage": self.storage,
            "neighbors": self.bootstrappable_k_closest(),
            "router": self.router,
        }
        with open(fname, "wb") as f:
            pickle.dump(data, f)

    async def lookup(self, id):
        """Realiza una búsqueda para encontrar los k nodos más cercanos a un ID"""
        log.info(f"Initiating lookup for key {id}")
        node = NodeData(id=id)

        # Inicializar el conjunto de nodos más cercanos a partir de la tabla de enrutamiento
        nearest = SortedList(
            [
                (distance_to(id, contact.id), contact)
                for contact in self.router.k_closest_to(node.id)
            ]
        )
        if not nearest:
            log.warning(f"No known neighbors to lookup key {id}")
            return []

        # Iniciar las consultas a los alpha nodos más cercanos
        already_queried = set()

        while True:
            responses = []
            # Seleccionamos hasta alpha nodos para consultar simultáneamente
            tasks = [
                self.call_find_node(n, node)
                for _, n in nearest
                if not n.id in already_queried
            ]
            nodes_to_query = [n for _, n in nearest if not n.id in already_queried]
            results = await asyncio.gather(*tasks)
            results = zip(results, nodes_to_query)

            for result, n in results:
                if result[0]:
                    responses.extend([NodeData(n.ip, n.port, n.id) for n in result[1]])

            for n in responses:
                if n.id not in already_queried:
                    nearest.add(distance_to(n.id, id), n)
                    already_queried.add(n.id)

            nearest = nearest[: self.ksize]
            if all(x in already_queried for x in nearest):
                break

        return nearest

    @classmethod
    async def load_state(cls, fname, port, interface="0.0.0.0"):
        """Carga el estado del nodo desde un archivo"""
        log.info(f"Loading state from {fname}")
        with open(fname, "rb") as f:
            data = pickle.load(f)

        node = cls(
            node_id=data["id"],
            storage=data["storage"],
            ip=interface,
            port=port,
            ksize=data["ksize"],
            alpha=data["alpha"],
        )
        node.router = data["router"]
        await node.listen(port, interface)
        if data["neighbors"]:
            await node.bootstrap(data["neighbors"])
        return node

    def refresh_table(self):
        """Refresca la tabla de enrutamiento periódicamente"""
        log.debug("Refreshing routing table")
        asyncio.ensure_future(self._refresh_table())
        loop = asyncio.get_event_loop()
        # para qeu la tabla de enrutamiento se refresque cada 30 segundos
        self.refresh_loop = loop.call_later(30, self.refresh_table)

    async def _refresh_table(self):
        """Actualiza la tabla de enrutamiento buscando nodos refrescados"""
        # for node_id in self.protocol.get_refresh_ids():
        #     node = NodeData(node_id)
        #     nearest = self.router.k_closest_to(node)
        #     # Aquí puedes agregar la lógica para refrescar la tabla


def distance_to(node_1_id, node_2_id):
    # Calcula la distancia de un nodo a otro nodo usando XOR
    return node_1_id ^ node_2_id
