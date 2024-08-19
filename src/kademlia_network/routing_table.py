from kBucket import KBucket
from sortedcontainers import SortedList

class Routing_Table:
    def __init__(self, owner_node, bucket_max_size):
        self.buckets = SortedList([KBucket(owner_node, bucket_max_size, 0, (1<<160))], key= lambda kbucket : kbucket.start)
        self.owner_node = owner_node
        self.bucket_max_size = bucket_max_size
    
    def add(self, node) -> None:
        bucket = self.buckets[self.buckets.bisect_left(node)]
        if bucket.add(node):
            return
        if bucket.can_be_splitted:
            left_bucket, right_bucket = bucket.split()
            self.buckets.discard(bucket)
            self.buckets.add(left_bucket)
            self.buckets.add(right_bucket)
    
    def k_closest_to(self, node):
        bucket_idx = self.bucket_idx_of(node)
        closest = [(node.id ^ contact.id, contact) for contact in self.buckets[bucket_idx].get_contacts()]
        i = 1
        while len(closest) < self.bucket_max_size:
            if bucket_idx >= i:
                closest.extend([(node.id ^ contact.id, contact) for contact in self.buckets[bucket_idx - i].get_contacts()])
            if bucket_idx + i < len(self.buckets):
                closest.extend([(node.id ^ contact.id, contact) for contact in self.buckets[bucket_idx + i].get_contacts()])
        closest.sort()
        return [contact for distance, contact in closest[:self.bucket_max_size]]
    
    def bucket_idx_of(self, node):
        return self.buckets.bisect_left(node)
    
    def __contains__(self, node):
        return self.buckets[self.bucket_idx_of(node)].__contains__(node)