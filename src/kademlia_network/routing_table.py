from kBucket import KBucket
from sortedcontainers import SortedList
from src.kademlia_network.Kdemlia_Node import Node
from src.kademlia_network.node_data import NodeData


class Routing_Table:
    def __init__(self, owner_node: Node, bucket_max_size):
        self.buckets = SortedList(
            [KBucket(owner_node, bucket_max_size, 0, (1 << 160))],
            key=lambda kbucket: kbucket.start,
        )
        self.owner_node = owner_node
        self.bucket_max_size = bucket_max_size
    
    def add(self, node) -> None:
        bucket = self.bucket_of(node)
        if bucket.add(node):
            return
        if bucket.can_be_splitted:
            left_bucket, right_bucket = bucket.split()
            self.buckets.discard(bucket)
            self.buckets.add(left_bucket)
            self.buckets.add(right_bucket)
    
    def remove(self, node) -> None:
        self.bucket_of(node).remove(node)
    
    def k_closest_to(self, node):
        bucket_idx = self.bucket_of(node, True)
        closest = [((inactive, node.id ^ contact.id), contact) for inactive, contact in self.buckets[bucket_idx].get_contacts()]
        i = 1
        while (len(closest) < self.bucket_max_size) or closest[self.bucket_max_size][0][0]:
            previous_len = len(closest)
            if bucket_idx >= i:
                closest.extend([((inactive, node.id ^ contact.id), contact) for inactive, contact in self.buckets[bucket_idx - i].get_contacts()])
            if bucket_idx + i < len(self.buckets):
                closest.extend([((inactive, node.id ^ contact.id), contact) for inactive, contact in self.buckets[bucket_idx + i].get_contacts()])
            if len(closest) == previous_len:#No hay nada mas que add
                break
            i += 1
        closest.sort()
        return [contact for _, contact in closest[:self.bucket_max_size]]
    
    def bucket_of(self, node, just_get_idx = False):
        if just_get_idx:
            return self.buckets.bisect_left(node)
        return self.buckets[self.buckets.bisect_left(node)]
    
    def __contains__(self, node):
        return self.bucket_of(node).__contains__(node)
