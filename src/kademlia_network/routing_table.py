from src.kademlia_network.kBucket import KBucket
from sortedcontainers import SortedList
from src.kademlia_network.node_data import NodeData
from typing import List

n_of_bits = 4


class Routing_Table:
    def __init__(self, owner_node, bucket_max_size: int):
        self.owner_node = owner_node
        self.buckets = [KBucket(owner_node, bucket_max_size)] * n_of_bits
        self.bucket_max_size = bucket_max_size

    async def add(self, node: NodeData) -> bool:
        return await self.bucket_of(node.id).add(node)

    def remove(self, id: int) -> None:
        self.bucket_of(id).remove(id)

    def k_closest_to(self, id: int) -> List[NodeData]:
        distance = id ^ self.owner_node.id
        closest = []
        for i in range(n_of_bits - 1, -1, -1):
            value = distance & (1 << i)
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
            for i in range(0, n_of_bits):
                if not distance & (1 << i):
                    closest.extend(
                        [
                            (id ^ contact.id, contact)
                            for contact in self.buckets[i].get_contacts()
                        ]
                    )
        closest.sort()
        return [contact for _, contact in closest[: self.bucket_max_size]]

    def bucket_of(self, id: int) -> KBucket:
        return self.buckets[(self.owner_node.id ^ id).bit_length() - 1]

    def __contains__(self, id: int) -> bool:
        return id in self.bucket_of(id)

    def __str__(self) -> str:
        result = []
        for index, k_buckets in enumerate(self.buckets):
            result.append(f"Kbucket {index}")
            for contact in k_buckets.get_contacts():
                result.append(f"{contact.id}")
            result.append("======================== \n")
        return "\n".join(result)
