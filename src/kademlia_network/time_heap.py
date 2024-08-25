from collections import deque
import logging

log = logging.getLogger(__name__)


class Time_Heap:
    def __init__(
        self,
    ):
        self.heap = deque()
        self.times_in_heap = {}

    def add_vision(self, id: int) -> None:
        self.heap.append(id)
        self.times_in_heap[id] = self.times_in_heap.get(id, 0) + 1

    def get_least_seen(self) -> int:
        """Devuelve el id del nodo que fue visto por ultima vez hace mas tiempo"""
        id = self.heap.popleft()
        while self.times_in_heap[id] != 1:
            self.times_in_heap[id] = max(self.times_in_heap[id] - 1, 0)
            id = self.heap.popleft()
        self.remove(id)
        return id

    def remove(self, id):
        self.times_in_heap[id] = 0
