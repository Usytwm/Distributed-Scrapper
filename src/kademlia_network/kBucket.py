import logging
import asyncio
from typing import List, Dict, Tuple
from src.kademlia_network.node_data import NodeData
from src.kademlia_network.time_heap import Time_Heap

log = logging.getLogger(__name__)


class KBucket:
    def __init__(
        self,
        owner_node,
        bucket_max_size: int,
    ):
        self.owner_node = owner_node
        self.max_size = bucket_max_size
        self.contacts: Dict = {}
        self.time_heap = Time_Heap()

    async def add(self, node: NodeData) -> bool:
        """Retorna True si el nodo fue anhadido y False si fue descartado"""
        lock = asyncio.Lock()
        async with lock:
            if node.id in self.contacts:
                self.time_heap.add_vision(node.id)
                return True
            if len(self.contacts) == self.max_size:
                answered, least_seen_id = await self.__check_least_seen_node__()
                # if answered == False:
                #     log.error("Dio falso")
                if answered:
                    self.time_heap.add_vision(least_seen_id)
                    return False
                else:
                    self.remove(least_seen_id)
            self.time_heap.add_vision(node.id)
            self.contacts[node.id] = node
            return True

    def remove(self, id) -> None:
        self.time_heap.remove(id)
        self.contacts.pop(id)

    def get_contacts(self):
        return list(self.contacts.values())

    def __contains__(self, id):
        return id in self.contacts

    async def __check_least_seen_node__(self) -> bool:
        # async with self._lock:
        id = self.time_heap.get_least_seen()
        ping_result = await self.owner_node.call_ping(self.contacts[id])
        return ping_result, id
