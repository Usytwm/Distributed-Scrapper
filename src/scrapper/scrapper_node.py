import logging
import os
import signal
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from threading import Thread
from typing import List
from kademlia_network.kademlia_heap_node import KademliaHeapNode
from src.kademlia_network.kademlia_node_data import KademliaNodeData

log = logging.getLogger(__name__)


class Scrapper_Node(KademliaHeapNode):
    def __init__(self, host, port):
        super().__init__(host=host, port=port)
        self.configure_scrapper_endpoints()

    def configure_scrapper_endpoints(self):
        @self.app.route("/scrap")
        def scrap():
            data = request.get_json(force=True)
            url = data.get("url")
            return self.scrap(url)

        @self.app.route("/leader/update_admins_entry_points")
        def update_admins_entry_points_as_leader():
            data = request.get_json(force=True)
            register_idx = data.get("register_idx")
            entry_points = [
                KademliaNodeData.from_json(node) for node in data.get("entry points")
            ]
            response = self.update_admins_entry_points_as_leader(
                entry_points, register_idx
            )
            return jsonify(response), 200

    def update_admins_entry_points_as_leader(
        self, entry_points: List[KademliaNodeData], register_idx: int
    ):
        idx = self.get_length("entry points") - 1
        while idx > register_idx:
            node = self.list_get(idx)
            address = f"{node.ip}:{node.port}"
            response = self.call_rpc(address, "global_ping", {})
            if response and response.get("status") == "OK":
                break
            self.pop_as_leader("entry points")
            idx -= 1
        for entry_point in entry_points:
            self.push("entry points", entry_point.to_json())
        return {"status": "OK"}

    def register(self, entry_points: List[KademliaNodeData]):
        """Este metodo une el scrapper a la red. Toma como parametro la direccion de otros nodos scrapper que
        usara para el bootstrapping. Una vez en la red podra conocer a que entry_points de la red de administradores
        puede solicitarle su registro"""
        self.bootstrap(entry_points)
        idx = self.get_length("entry points") - 1
        while idx >= 0:
            entry_point = KademliaNodeData.from_json(self.list_get(idx))
            address = f"{entry_point.ip}:{entry_point.port}"
            data = {"role": "scrapper", "node": self.node_data.to_json()}
            response = self.call_rpc(address, "follower/register", data)
            if response and response.get("status") == "OK":
                address = self.find_leader_address()
                data = {
                    "register_idx": idx,
                    "entry points": response.get("entry points"),
                }
                self.call_rpc(address, "leader/update_admins_entry_points", data)
                break
            idx -= 1
        return idx >= 0

    def scrap(self, url: str, format="html"):
        try:
            # Solicitar la página web
            response = requests.get(url)
            response.raise_for_status()  # Verificar que la solicitud fue exitosa

            # Parsear el contenido de la página
            soup = BeautifulSoup(response.text, "html.parser")

            # Usar match-case para seleccionar el formato de retorno
            match format:
                case "text":
                    structured_content = soup.get_text()
                case "html":
                    structured_content = str(soup)
                case _:
                    structured_content = str(soup)  # Por defecto, devolver HTML

            # Extraer todos los enlaces de la página
            links = []
            for link in soup.find_all("a", href=True):
                # Asegurar que los enlaces sean completos (absolutos)
                full_link = urljoin(url, link["href"])
                links.append(full_link)

            return jsonify({"content": structured_content, "links": links}), 200

        except requests.exceptions.RequestException as e:
            log.error(f"Error al solicitar la URL: {e}")
            return jsonify({"error": str(e)}), 500

        except Exception as e:
            log.error(f"Unexpected error: {e}")
            return jsonify({"error": "Internal server error"}), 500
