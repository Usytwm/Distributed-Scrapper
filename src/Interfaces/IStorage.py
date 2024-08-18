from abc import ABC, abstractmethod


class IStorage(ABC):
    @abstractmethod
    def __setitem__(self, key, value):
        # Almacena un valor con la clave dada
        pass

    @abstractmethod
    def __getitem__(self, key):
        # Devuelve el valor almacenado con la clave dada
        pass

    @abstractmethod
    def get(self, key, default=None):
        # Devuelve el valor almacenado con la clave dada o un valor por defecto
        pass

    @abstractmethod
    def iter_older_than(self, seconds_old):
        # Itera sobre los elementos más antiguos que el tiempo especificado
        pass

    @abstractmethod
    def __iter__(self):
        # Itera sobre todos los elementos almacenados
        pass
