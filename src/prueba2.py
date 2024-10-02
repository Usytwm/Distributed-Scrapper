import logging
from pathlib import Path
import sys
import time
import requests


path_to_root = Path(__file__).resolve().parents[1]
sys.path.append(str(path_to_root))


from src.administration.admin_node import Admin_Node
from src.scrapper.scrapper_node import Scrapper_Node
from src.storage.storage_node import StorageNode

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

    admin_node_3 = Admin_Node(ip="127.0.0.1", port=8003)
    admin_node_3.listen()
    admin_node_3.start()

    scrapper_node_0 = Scrapper_Node(host="127.0.0.1", port=9000)
    scrapper_node_0.listen()
    scrapper_node_0.start()

    scrapper_node_1 = Scrapper_Node(host="127.0.0.1", port=9001)
    scrapper_node_1.listen()
    scrapper_node_1.start()

    scrapper_node_2 = Scrapper_Node(host="127.0.0.1", port=9002)
    scrapper_node_2.listen()
    scrapper_node_2.start()

    scrapper_node_3 = Scrapper_Node(host="127.0.0.1", port=9003)
    scrapper_node_3.listen()
    scrapper_node_3.start()

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

    data = {
        "url": "https://example.com",
    }
    response = requests.post("http://127.0.0.1:8002/push_url", json=data)

    queries = [
        "https://example.com",
        "https://www.iana.org/domains/example",
        "https://www.iana.org/",
        "https://www.iana.org/about",
        # "https://www.iana.org/help/example-domains",
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

    x = storage_node_3.get("https://example.com")
    y = storage_node_1.get("https://www.iana.org/domains/example")
    b = storage_node_0.get("http://www.iana.org/help/example-domains")


if __name__ == "__main__":
    main()
