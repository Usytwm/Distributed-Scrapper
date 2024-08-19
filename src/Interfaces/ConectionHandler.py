import rpyc
import logging

log = logging.getLogger(__name__)


class ConnectionHandler(rpyc.Service):
    """Clase base que maneja las conexiones de RPyC"""

    def on_connect(self, conn):
        """Se llama cuando un cliente se conecta"""
        log.info(f"Cliente conectado desde {conn._channel.stream.sock.getpeername()}")

    def on_disconnect(self, conn):
        """Se llama cuando un cliente se desconecta"""
        log.info(
            f"Cliente desconectado desde {conn._channel.stream.sock.getpeername()}"
        )

    def _ping(self, address, node_id):
        """Método interno para manejar PING"""
        with rpyc.connect(address[0], address[1]) as conn:
            return conn.root.ping(node_id)

    def _store(self, address, node_id, key, value):
        """Método interno para manejar STORE"""
        with rpyc.connect(address[0], address[1]) as conn:
            return conn.root.store(node_id, key, value)

    def _find_node(self, address, node_id, key):
        """Método interno para manejar FIND_NODE"""
        with rpyc.connect(address[0], address[1]) as conn:
            return conn.root.find_node(node_id, key)

    def _find_value(self, address, node_id, key):
        """Método interno para manejar FIND_VALUE"""
        with rpyc.connect(address[0], address[1]) as conn:
            return conn.root.find_value(node_id, key)
