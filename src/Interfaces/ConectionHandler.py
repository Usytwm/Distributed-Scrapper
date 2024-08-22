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
        try:
            self.conn.close()
            log.info(
                f"Cliente desconectado desde {conn._channel.stream.sock.getpeername()}"
            )
        except EOFError:
            log.warning("Intento de acceso a un stream cerrado")
        except Exception as e:
            log.error(f"Error al desconectar cliente: {e}")

    def _ping(self, address, node):
        """Método interno para manejar PING"""
        try:
            with rpyc.connect(
                address[0], address[1], config={"sync_request_timeout": 10}
            ) as conn:
                return conn.root.ping(node)
        except Exception as e:
            log.error(f"Error en _ping: {e}")
            return None

    def _store(self, address, node, key, value):
        """Método interno para manejar STORE"""
        try:
            with rpyc.connect(
                address[0], address[1], config={"sync_request_timeout": 10}
            ) as conn:
                return conn.root.store(node, key, value)
        except Exception as e:
            log.error(f"Error en _find_node: {e}")
            return None

    def _find_node(self, address, node, key):
        """Método interno para manejar FIND_NODE"""
        try:
            with rpyc.connect(
                address[0], address[1], config={"sync_request_timeout": 10}
            ) as conn:
                return conn.root.find_node(node, key)
        except Exception as e:
            log.error(f"Error en _find_node: {e}")
            return None

    def _find_value(self, address, node, key):
        """Método interno para manejar FIND_VALUE"""
        try:
            with rpyc.connect(
                address[0], address[1], config={"sync_request_timeout": 10}
            ) as conn:
                return conn.root.find_value(node, key)
        except Exception as e:
            log.error(f"Error en _find_value: {e}")
            return None
