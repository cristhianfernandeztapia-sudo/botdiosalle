import os
import json

def cargar_memoria(chat_id):
    archivo = f"memoria/{chat_id}.json"
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_memoria(chat_id, datos):
    os.makedirs("memoria", exist_ok=True)
    archivo = f"memoria/{chat_id}.json"
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
