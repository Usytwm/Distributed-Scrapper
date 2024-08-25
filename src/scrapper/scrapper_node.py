import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from threading import Thread

import requests

log = logging.getLogger(__name__)


class Scrapper_Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.configure_endpoints()

    def listen(self):
        def run_app():
            self.app.run(host=self.host, port=self.port, threaded=True)

        thread = Thread(target=run_app)
        thread.start()

    def stop(self):
        pass

    def configure_endpoints(self):
        @self.app.route("/scrap")
        def scrap():
            data = request.get_json(force=True)
            url = data.get("url")
            response = self.scrap(url)
            return jsonify(response), 200

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

            return {"content": structured_content, "links": links}

        except requests.exceptions.RequestException as e:
            log.error(f"Error al solicitar la URL: {e}")
            return {"error": str(e)}, 500
