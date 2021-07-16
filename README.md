# pyChain
A simple blockchain implementation in Python

# Instrucciones de uso

__Estas instrucciones son para levantar dos clientes que interactúan entre si, si se desea levantar más es cuestión de repetir los pasos pertinentes al puerto 8001__

 - Clonar el repositorio y ejecutar en la consola:
 - `. venv/bin/activate`
 - `flask run --port=8000`, esto levanta nuestro puerto principal.
 - `flask run --port=8001`, levanta un cliente más
 - Subscribo al cliente 8001:
  ```
  curl -X POST \
  http://127.0.0.1:8001/register \
  -H 'Content-Type: application/json' \
  -d '{"node_address": "http://127.0.0.1:8000"}'
  ```
  - Listo, ya se puede empezar a jugar!
