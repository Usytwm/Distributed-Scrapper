# Distributed-Scrapper

A distributed web scraping network that utilizes specialized nodes for data collection, processing, and storage, ensuring high availability and resilience in extracting web information

| Nombre                     | Grupo | Github                                   |
| -------------------------- | ----- | ---------------------------------------- |
| Brián Ameht Inclán Quesada | C411  | [@Usytwm](https://github.com/Usytwm)     |
| Davier Sanchez Bello       | C411  | [@DavierSB](https://github.com/DavierSB) |

python levantar_nodo.py --type admin --ip 192.168.1.10 --port 8000
python levantar_nodo.py --type scrapper --ip 192.168.1.11 --port 8100
python levantar_nodo.py --type storage --ip 192.168.1.12 --port 8200
python levantar_nodo.py --type admin --ip 127.0.0.1 --port 8000
