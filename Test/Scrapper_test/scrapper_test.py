import logging
import sys
from pathlib import Path

from src.scrapper.scrapper_node import Scrapper_Node

path_to_root = Path(__file__).resolve().parents[2]
sys.path.append(str(path_to_root))

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_scrap_html():
    """
    Prueba el scrapper con una URL válida y formato HTML.
    """
    scrapper = Scrapper_Node(host="127.0.0.1", port=9000)
    test_url = "http://example.com"

    # Ejecutar el método de scrap con formato "html"
    response_content, status_code = scrapper.scrap(test_url, format="html")

    # Verificar que el estado es 200
    assert (
        status_code == 200
    ), f"Fallo: Código de estado incorrecto, esperado 200, obtenido {status_code}"

    # Verificar que el contenido tiene etiquetas HTML
    assert (
        "<html>" in response_content["content"]
    ), "Fallo: El contenido devuelto no contiene el HTML esperado"
    log.info("Test scrap_html pasado correctamente.")


def test_scrap_text():
    """
    Prueba el scrapper con una URL válida y formato texto.
    """
    scrapper = Scrapper_Node(host="localhost", port=9001)
    test_url = "http://example.com"

    # Ejecutar el método de scrap con formato "text"
    response_content, status_code = scrapper.scrap(test_url, format="text")

    # Verificar que el estado es 200
    assert (
        status_code == 200
    ), f"Fallo: Código de estado incorrecto, esperado 200, obtenido {status_code}"

    # Verificar que el contenido no tiene etiquetas HTML
    assert (
        "<html>" not in response_content["content"]
    ), "Fallo: El contenido devuelto contiene HTML cuando no debería"
    log.info("Test scrap_text pasado correctamente.")


def test_invalid_url():
    """
    Prueba el scrapper con una URL inválida.
    """
    scrapper = Scrapper_Node(host="localhost", port=9002)
    test_url = "http://invalid-url"

    # Ejecutar el método de scrap con una URL inválida
    response_content, status_code = scrapper.scrap(test_url, format="html")

    # Verificar que el código de estado es 500
    assert (
        status_code == 500
    ), f"Fallo: Código de estado incorrecto, esperado 500, obtenido {status_code}"
    log.info("Test invalid_url pasado correctamente.")


def test_extract_links():
    """
    Prueba el scrapper para la extracción de enlaces.
    """
    scrapper = Scrapper_Node(host="localhost", port=9003)
    test_url = "http://example.com"

    # Ejecutar el método de scrap para extraer links
    response_content, status_code = scrapper.scrap(test_url, format="html")

    # Verificar que el estado es 200
    assert (
        status_code == 200
    ), f"Fallo: Código de estado incorrecto, esperado 200, obtenido {status_code}"

    # Verificar que la lista de enlaces no está vacía
    assert response_content.get("links"), "Fallo: No se extrajeron enlaces"
    log.info("Test extract_links pasado correctamente.")


def test_scrap_json():
    """
    Prueba el scrapper con un formato no soportado.
    """
    scrapper = Scrapper_Node(host="localhost", port=9004)
    test_url = "http://example.com"

    # Ejecutar el método de scrap con un formato no válido
    response_content, status_code = scrapper.scrap(test_url, format="json")

    # Verificar que el contenido devuelto es HTML por defecto
    assert (
        "<html>" in response_content["content"]
    ), "Fallo: No devolvió el HTML por defecto"
    log.info("Test scrap_json (formato no soportado) pasado correctamente.")


def test_empty_url():
    """
    Prueba el scrapper con una URL vacía.
    """
    scrapper = Scrapper_Node(host="localhost", port=9005)
    test_url = ""

    # Ejecutar el método de scrap con una URL vacía
    response_content, status_code = scrapper.scrap(test_url, format="html")

    # Verificar que el código de estado es 500 (error interno)
    assert (
        status_code == 500
    ), f"Fallo: Código de estado incorrecto, esperado 500, obtenido {status_code}"
    log.info("Test empty_url pasado correctamente.")


def test_url_redirection():
    """
    Prueba el scrapper para manejar redirecciones.
    """
    scrapper = Scrapper_Node(host="localhost", port=9006)
    test_url = "http://httpbin.org/redirect-to?url=http://example.com"

    # Ejecutar el método de scrap con una URL que redirige
    response_content, status_code = scrapper.scrap(test_url, format="html")

    # Verificar que el estado es 200
    assert (
        status_code == 200
    ), f"Fallo: Código de estado incorrecto, esperado 200, obtenido {status_code}"

    # Verificar que el contenido tiene etiquetas HTML de la página final
    assert (
        "<html>" in response_content["content"]
    ), "Fallo: El contenido devuelto no contiene el HTML esperado"
    log.info("Test url_redirection pasado correctamente.")


if __name__ == "__main__":
    test_scrap_html()
    test_scrap_text()
    test_invalid_url()
    test_extract_links()
    test_scrap_json()
    test_empty_url()
    test_url_redirection()
