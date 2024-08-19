from collections import deque
class Time_Heap:
    def __init__(self):
        self.heap = deque()
        self.times_in_heap = {}
    
    def add_vision(self, id):
        self.heap.append(id)
        self.times_in_heap[id] = self.times_in_heap.get(id, 0) + 1
    
    def get_least_seen(self):
        id = deque.popleft()
        while self.times_in_heap[id] != 1:
            self.times_in_heap[id] = min(self.times_in_heap[id] - 1, 0)
            id = deque.popleft()
        self.times_in_heap[id] = 0
        return id
    
    def split(self, mid):
        left = Time_Heap()
        right = Time_Heap()
        for id in self.heap:
            (left if id <= mid else right).add_vision(right)
        return (left, right)