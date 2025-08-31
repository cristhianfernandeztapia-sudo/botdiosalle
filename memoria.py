import os
import json

def cargar_memoria(chat_id):
    archivo = f"memoria/{chat_id}.json"
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
                historial = datos.get("historial", [])

                # Validar estructura de historial
                historial_valido = [
                    m for m in historial
                    if isinstance(m, dict) and "role" in m and "content" in m
                ]

                return {"historial": historial_valido}
            except json.JSONDecodeError:
                print(f"[Error] JSON corrupto en {archivo}, se ignorará.")
                return {}
    return {}

def guardar_memoria(chat_id, datos):
    os.makedirs("memoria", exist_ok=True)

    # Validar antes de guardar
    historial = datos.get("historial", [])
    historial_valido = [
        m for m in historial
        if isinstance(m, dict) and "role" in m and "content" in m
    ]

    archivo = f"memoria/{chat_id}.json"
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump({"historial": historial_valido}, f, indent=2, ensure_ascii=False)
