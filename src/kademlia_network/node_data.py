from collections import namedtuple
from typing import NamedTuple


class NodeData(NamedTuple):
    id: int
    ip: str = ""
    port: int = 0
