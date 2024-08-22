from src.kademlia_network.kBucket import KBucket
from sortedcontainers import SortedList
from src.kademlia_network.node_data import NodeData
from typing import List

n_of_bits = 4


class Routing_Table:
    def __init__(self, owner_node, bucket_max_size: int):
        self.buckets = {0: KBucket(owner_node, bucket_max_size, 0, (1 << n_of_bits))}
        self.bucket_starts = SortedList([0])
        self.owner_node = owner_node
        self.bucket_max_size = bucket_max_size

    def add(self, node: NodeData) -> bool:
        bucket = self.bucket_of(node.id)
        if bucket.add(node):
            return True
        if bucket.can_be_splitted:
            self.split_bucket(bucket)
            self.add(node)
        return False

    def remove(self, id: int) -> None:
        self.bucket_of(id).remove(id)

    def k_closest_to(self, id: int) -> List[NodeData]:
        bucket = self.bucket_of(id)
        closest = [(id ^ contact.id, contact) for contact in bucket.get_contacts()]
        i = 1
        while len(closest) < self.bucket_max_size:
            previous_len = len(closest)
            if bucket.id >= i:
                closest.extend(
                    [
                        (id ^ contact.id, contact)
                        for contact in self.buckets[bucket.id - i].get_contacts()
                    ]
                )
            if bucket.id + i < len(self.buckets):
                closest.extend(
                    [
                        (id ^ contact.id, contact)
                        for contact in self.buckets[bucket.id + i].get_contacts()
                    ]
                )
            if len(closest) == previous_len:  # No hay nada mas que add
                break
            i += 1
        closest.sort()
        return [contact for _, contact in closest[: self.bucket_max_size]]

    def bucket_of(self, id: int, just_get_idx=False) -> KBucket:
        try:
            print(self.bucket_starts)
            print(self.buckets)
            print(self.bucket_starts.bisect_right(id) - 1)
            return self.buckets[
                self.bucket_starts[self.bucket_starts.bisect_right(id) - 1]
            ]
        except Exception as e:
            print(f"Error: {e}")
            return None

    def split_bucket(self, bucket: KBucket):
        left_bucket, right_bucket = bucket.split()
        self.bucket_starts.remove(bucket.start)
        self.buckets.pop(bucket.start)
        self.bucket_starts.add(left_bucket.start)
        self.buckets[left_bucket.start] = left_bucket
        self.bucket_starts.add(right_bucket.start)
        self.buckets[right_bucket.start] = right_bucket

    def __contains__(self, id: int) -> bool:
        return self.bucket_of(id).__contains__(id)
