import asyncio
import heapq
import operator
import time

from src.kademlia_network.kBucket import KBucket


class RoutingTable:
    def __init__(self, protocol, ksize, node):
        # Inicializa la tabla de enrutamiento con el protocolo, tamaño k y nodo
        self.node = node
        self.protocol = protocol
        self.ksize = ksize
        self.flush()

    def flush(self):
        # Limpia y reinicia la tabla de enrutamiento
        self.buckets = [KBucket(0, 2**160, self.ksize)]

    def split_bucket(self, index):
        # Divide un bucket en dos
        one, two = self.buckets[index].split()
        self.buckets[index] = one
        self.buckets.insert(index + 1, two)

    def lonely_buckets(self):
        # Devuelve los buckets que no se han actualizado recientemente
        hrago = time.monotonic() - 3600
        return [b for b in self.buckets if b.last_updated < hrago]

    def remove_contact(self, node):
        # Elimina un contacto de la tabla de enrutamiento
        index = self.get_bucket_for(node)
        self.buckets[index].remove_node(node)

    def is_new_node(self, node):
        # Verifica si un nodo es nuevo en la tabla de enrutamiento
        index = self.get_bucket_for(node)
        return self.buckets[index].is_new_node(node)

    def add_contact(self, node):
        # Añade un contacto a la tabla de enrutamiento
        index = self.get_bucket_for(node)
        bucket = self.buckets[index]

        if bucket.add_node(node):
            return

        if bucket.has_in_range(self.node) or bucket.depth() % 5 != 0:
            self.split_bucket(index)
            self.add_contact(node)
        else:
            asyncio.ensure_future(self.protocol.call_ping(bucket.head()))

    def get_bucket_for(self, node):
        # Devuelve el índice del bucket que contiene al nodo
        for index, bucket in enumerate(self.buckets):
            if node.long_id < bucket.range[1]:
                return index
        return None

    def find_neighbors(self, node, k=None, exclude=None):
        # Encuentra los vecinos más cercanos a un nodo
        k = k or self.ksize
        nodes = []
        for neighbor in TableTraverser(self, node):
            notexcluded = exclude is None or not neighbor.same_home_as(exclude)
            if neighbor.id != node.id and notexcluded:
                heapq.heappush(nodes, (node.distance_to(neighbor), neighbor))
            if len(nodes) == k:
                break

        return list(map(operator.itemgetter(1), heapq.nsmallest(k, nodes)))
