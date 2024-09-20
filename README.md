# Distributed-Scrapper

A distributed web scraping network that utilizes specialized nodes for data collection, processing, and storage, ensuring high availability and resilience in extracting web information

| Nombre                     | Grupo | Github                                   |
| -------------------------- | ----- | ---------------------------------------- |
| Brián Ameht Inclán Quesada | C411  | [@Usytwm](https://github.com/Usytwm)     |
| Davier Sanchez Bello       | C411  | [@DavierSB](https://github.com/DavierSB) |

## Nodo Bootstrap admin

```bash
python src/main.py --type admin -i 127.0.0.1 -p 8000
```

### Nodo admin

```bash
python src/main.py --type admin -i 127.0.0.1 -p 8001 --bootstrap 127.0.0.1:8000
```

## Nodo Bootstrap scrapper

```bash
python src/main.py --type scrapper -i 127.0.0.1 -p 9000
```

### Nodo scrapper

```bash
python src/main.py --type scrapper -i 127.0.0.1 -p 9001 --bootstrap 127.0.0.1:9000
```

## Nodo Bootstrap storage

```bash
python src/main.py --type storage -i 127.0.0.1 -p 10000
```

### Nodo admin

```bash
python src/main.py --type storage -i 127.0.0.1 -p 10001 --bootstrap 127.0.0.1:10000
```

<!-- python src/main.py --type storage -i 127.0.0.1 -p 10001 --bootstrap 127.0.0.1:8000 -->
