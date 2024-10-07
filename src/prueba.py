import logging
from pathlib import Path
import sys
import time
import requests


path_to_root = Path(__file__).resolve().parents[1]
sys.path.append(str(path_to_root))


from src.utils.utils import kill_processes_on_port
from src.administration.admin_node import Admin_Node
from src.scrapper.scrapper_node import Scrapper_Node
from src.storage.storage_node import StorageNode


# Desactivar logs de urllib3
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# Desactivar logs de werkzeug (Flask)
logging.getLogger("werkzeug").setLevel(logging.CRITICAL)

logging.basicConfig(level=logging.CRITICAL)
log = logging.getLogger(__name__)
log.setLevel(logging.CRITICAL)


def main():
    admin_node_0 = Admin_Node(ip="127.0.0.1", port=8000)
    admin_node_0.listen()
    admin_node_0.start()

    admin_node_1 = Admin_Node(ip="127.0.0.1", port=8001)
    admin_node_1.listen()
    admin_node_1.start()

    admin_node_2 = Admin_Node(ip="127.0.0.1", port=8002)
    admin_node_2.listen()
    admin_node_2.start()

    scrapper_node_0 = Scrapper_Node(host="127.0.0.1", port=9000)
    scrapper_node_0.listen()
    scrapper_node_0.start()

    scrapper_node_1 = Scrapper_Node(host="127.0.0.1", port=9001)
    scrapper_node_1.listen()
    scrapper_node_1.start()

    storage_node_0 = StorageNode(host="127.0.0.1", port=10000)
    storage_node_0.listen()
    storage_node_0.start()

    storage_node_1 = StorageNode(host="127.0.0.1", port=10001)
    storage_node_1.listen()
    storage_node_1.start()

    storage_node_2 = StorageNode(host="127.0.0.1", port=10002)
    storage_node_2.listen()
    storage_node_2.start()

    storage_node_3 = StorageNode(host="127.0.0.1", port=10003)
    storage_node_3.listen()
    storage_node_3.start()
    log.critical(
        "==============================================================All nodes started=============================================================="
    )

    data = {
        "url": "https://example.com",
    }
    response = requests.post("http://127.0.0.1:8002/push_url", json=data)

    queries = [
        "https://example.com",
    ]
    answers = []
    while True:
        time.sleep(3)
        for url in queries[len(answers) :]:
            answer = storage_node_2.get(url)
            if not answer:
                break
            answers.append(answer)
        if len(answers) == len(queries):
            break

    kill_processes_on_port(8000)
    kill_processes_on_port(10002)
    kill_processes_on_port(10003)

    x = storage_node_0.get("https://example.com")

    storage_node_2 = StorageNode(host="127.0.0.1", port=10005)
    storage_node_2.listen()
    storage_node_2.start()

    storage_node_3 = StorageNode(host="127.0.0.1", port=10006)
    storage_node_3.listen()
    storage_node_3.start()

    admin_node_2 = Admin_Node(ip="127.0.0.1", port=8006)
    admin_node_2.listen()
    admin_node_2.start()

    y = storage_node_0.get("https://example.com")

    kill_processes_on_port(10001)
    kill_processes_on_port(10006)

    z = storage_node_0.get("https://example.com")

    log.info("final")


if __name__ == "__main__":
    main()
