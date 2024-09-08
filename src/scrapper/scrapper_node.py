import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from flask import jsonify, request
import requests

from src.Interfaces.WorkerNode import Worker_Node

log = logging.getLogger(__name__)


class Scrapper_Node(Worker_Node):
    def __init__(self, host, port):
        super().__init__(host=host, port=port)
        self.configure_scrapper_endpoints()

    def configure_scrapper_endpoints(self):
        @self.app.route("/scrap", methods=["POST"])
        def scrap():
            data = request.get_json(force=True)
            url = data.get("url")
            return self.scrap(url)

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
