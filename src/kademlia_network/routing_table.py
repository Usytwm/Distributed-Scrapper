from src.kademlia_network.kBucket import KBucket
from sortedcontainers import SortedList
from src.kademlia_network.node_data import NodeData
from typing import List
import random
from threading import Thread
from src.utils.utils import N_OF_BITS


class Routing_Table:
    def __init__(self, owner_node, bucket_max_size: int):
        self.owner_node = owner_node
        self.buckets = [KBucket(owner_node, bucket_max_size) for _ in range(N_OF_BITS)]
        self.bucket_max_size = bucket_max_size

    def add(self, node: NodeData) -> bool:
        return self.bucket_of(node.id).add(node)

    def poblate(self):
        id = 0
        while (id < N_OF_BITS) and (len(self.buckets[id].contacts) == 0):
            id += 1
        id += 1
        results = []

        def lookup_and_save(id):
            results.append(self.owner_node.lookup(id))

        threads = []
        while id < len(self.buckets):
            random_id = (
                random.randint((1 << id), (1 << (id + 1)) - 1) ^ self.owner_node.id
            )
            thread = Thread(target=lookup_and_save, args=(random_id,))
            threads.append(thread)
            thread.start()
            id += 1
        for thread in threads:
            thread.join()
        threads = []
        for result in results:
            for contact in result:
                if contact.id != self.owner_node.id:
                    thread = Thread(target=self.add, args=(contact,))
                    threads.append(thread)
                    thread.start()
        for thread in threads:
            thread.join()

    def remove(self, id: int) -> None:
        self.bucket_of(id).remove(id)

    def k_closest_to(self, id: int) -> List[NodeData]:
        distance = id ^ self.owner_node.id
        closest = []
        for i in range(N_OF_BITS - 1, -1, -1):
            if distance & (1 << i):
                closest.extend(
                    [
                        (id ^ contact.id, contact)
                        for contact in self.buckets[i].get_contacts()
                    ]
                )
                if len(closest) >= self.bucket_max_size:
                    break
        if len(closest) < self.bucket_max_size:
            for i in range(0, N_OF_BITS):
                if not distance & (1 << i):
                    closest.extend(
                        [
                            (id ^ contact.id, contact)
                            for contact in self.buckets[i].get_contacts()
                        ]
                    )
        closest.append((self.owner_node.id ^ id, self.owner_node.node_data))
        closest.sort()
        return [contact for _, contact in closest[: self.bucket_max_size]]

    def bucket_of(self, id: int) -> KBucket:
        return self.buckets[(self.owner_node.id ^ id).bit_length() - 1]

    def __contains__(self, id: int) -> bool:
        return id in self.bucket_of(id)

    def get_contacts(self) -> List[NodeData]:
        contacts = []
        for k_bucket in self.buckets:
            contacts.extend(k_bucket.get_contacts())
        return contacts

    def __str__(self) -> str:
        result = []
        for index, k_buckets in enumerate(self.buckets):
            result.append(f"Kbucket {index}")
            for contact in k_buckets.get_contacts():
                result.append(f"{contact.id}")
            result.append("======================== \n")
        return "\n".join(result)
