
import json
import os

ARCHIVO_MEMORIA = "memoria.json"

# Cargar memoria existente (si existe)
if os.path.exists(ARCHIVO_MEMORIA):
    with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
        memoria = json.load(f)
else:
    memoria = {}

def recordar(clave: str, valor: str):
    """Guarda una clave y su valor en la memoria."""
    memoria[clave] = valor
    with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, indent=2, ensure_ascii=False)

def obtener_recuerdos():
    """Devuelve la memoria completa como diccionario."""
    return memoria
