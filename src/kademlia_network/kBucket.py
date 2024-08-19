from typing import List, Dict, Tuple
from time_heap import Time_Heap

class KBucket:
    def __init__(self, owner_node, bucket_max_size : int, start, end):
        self.owner_node = owner_node
        self.max_size = bucket_max_size
        self.start = start
        self.end = end
        self.contacts : Dict = {}
        self.time_heap = Time_Heap()
    
    def add(self, node) -> None:
        if node.id in self.contacts:
            self.time_heap.add_vision(node.id)
            return
        if len(self.contacts) == self.max_size:
            answered, least_seen_id = self.__check_least_seen_node__()
            if answered:
                self.time_heap.add_vision(least_seen_id)
                return
        self.time_heap.add_vision(node.id)
        self.contacts[node.id] = node
    
    def split(self) -> Tuple['KBucket', 'KBucket']:
        mid = (self.start + self.end) // 2
        left = KBucket(self.owner_node, self.max_size, self.start, self.mid)
        right = KBucket(self.owner_node, self.max_size, self.mid + 1, self.end)
        for node in self.contacts.values():
            if node.id <= mid:
                left.add(node)
            else:
                right.add(node)
        return (left, right)

    def __check_least_seen_node__(self) -> bool:
        id = self.time_heap.get_least_seen()
        return self.owner_node.ping(self.contacts[id]), id