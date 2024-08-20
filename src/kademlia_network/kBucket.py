from typing import List, Dict, Tuple
from time_heap import Time_Heap

class KBucket:
    def __init__(self, owner_node, bucket_max_size : int, start, end, can_be_splitted = True):
        self.owner_node = owner_node
        self.max_size = bucket_max_size
        self.start = start
        self.end = end
        self.contacts : Dict = {}
        self.time_heap = Time_Heap()
        self.can_be_splitted = can_be_splitted
    
    def add(self, node) -> bool:
        """Retorna True si el nodo fue anhadido y False si fue descartado"""
        if node.id in self.contacts:
            self.time_heap.add_vision(node.id)
            return True
        if len(self.contacts) == self.max_size:
            answered, least_seen_id = self.__check_least_seen_node__()
            if answered:
                self.time_heap.add_vision(least_seen_id)
                return False
            else:
                self.contacts.remove(least_seen_id)
        self.time_heap.add_vision(node.id)
        self.contacts[node.id] = node
        return True
    
    def remove(self, node) -> None:
        self.time_heap.mark_as_inactive(node.id)
    
    def split(self) -> Tuple['KBucket', 'KBucket']:
        mid = (self.start + self.end) // 2
        left = KBucket(self.owner_node, self.max_size, self.start, self.mid, (self.owner_node.id <= mid))
        right = KBucket(self.owner_node, self.max_size, self.mid + 1, self.end, (self.owner_node.id > mid))
        left_time_heap, right_time_heap = self.time_heap.split(mid)
        for node in self.contacts.values():
            if node.id <= mid:
                left.add(node)
            else:
                right.add(node)
        left.time_heap = left_time_heap
        right.time_heap = right_time_heap
        return (left, right)
    
    def get_contacts(self):
        return list(self.contacts.values())
    
    def __contains__(self, node):
        return node.id in self.contacts

    def __check_least_seen_node__(self) -> bool:
        id = self.time_heap.get_least_seen()
        return self.owner_node.ping(self.contacts[id]), id
    
# Los metodos a continuacion para poder trabajar con SorteList
    def __eq__(self, other):
        return (self.start == other.start)
    
    def __hash__(self) -> int:
        return hash(self.start)
    
    def __lt__(self, other):
        return self.start < other.start