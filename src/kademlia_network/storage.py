import sqlite3
import time
from src.Interfaces import IStorage


class Storage(IStorage):
    def __init__(self, db_file="kademlia_storage.db", ttl=604800):
        self.db_file = db_file
        self.ttl = ttl
        self.conn = sqlite3.connect(self.db_file)
        self._setup_table()

    def _setup_table(self):
        """Crea la tabla de almacenamiento si no existe."""
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS storage (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    timestamp REAL
                )
            """
            )

    def __setitem__(self, key, value):
        """Almacena un valor con la clave dada."""
        timestamp = time.time()
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO storage (key, value, timestamp)
                VALUES (?, ?, ?)
            """,
                (key, sqlite3.Binary(value), timestamp),
            )
        self.cull()

    def __getitem__(self, key):
        """Devuelve el valor almacenado con la clave dada."""
        self.cull()
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM storage WHERE key = ?", (key,))
        result = cur.fetchone()
        if result is None:
            raise KeyError(f"Key {key} not found")
        return result[0]

    def get(self, key, default=None):
        """Devuelve un valor almacenado con la clave dada o un valor por defecto."""
        try:
            return self[key]
        except KeyError:
            return default

    def cull(self):
        """Elimina los elementos que han superado el TTL."""
        expiration_time = time.time() - self.ttl
        with self.conn:
            self.conn.execute(
                "DELETE FROM storage WHERE timestamp < ?", (expiration_time,)
            )

    def iter_older_than(self, seconds_old):
        """Itera sobre los elementos más antiguos que el tiempo especificado."""
        cur = self.conn.cursor()
        cutoff = time.time() - seconds_old
        cur.execute("SELECT key, value FROM storage WHERE timestamp < ?", (cutoff,))
        return cur.fetchall()

    def __iter__(self):
        """Itera sobre todos los elementos almacenados."""
        self.cull()
        cur = self.conn.cursor()
        cur.execute("SELECT key, value FROM storage")
        return cur.fetchall()

    def __del__(self):
        """Cierra la conexión a la base de datos al finalizar."""
        self.conn.close()
