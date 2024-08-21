from collections import deque
from typing import Tuple


class Time_Heap:
    def __init__(self):
        self.heap = deque()
        self.times_in_heap = {}

    def add_vision(self, id: int) -> None:
        self.heap.append(id)
        self.times_in_heap[id] = self.times_in_heap.get(id, 0) + 1

    def get_least_seen(self) -> int:
        """Devuelve el id del nodo que fue visto por ultima vez hace mas tiempo"""
        id = deque.popleft()
        while self.times_in_heap[id] != 1:
            self.times_in_heap[id] = min(self.times_in_heap[id] - 1, 0)
            id = deque.popleft()
        self.remove(id)
        return id

    def split(self, mid: int) -> Tuple["Time_Heap", "Time_Heap"]:
        left = Time_Heap()
        right = Time_Heap()
        for id in self.heap:
            (left if id <= mid else right).add_vision(right)
        return (left, right)

    def remove(self, id):
        self.times_in_heap[id] = 0
