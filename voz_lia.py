
# voz_lia.py

import random

def generar_voz(texto):
    efectos = []

    # Susurros
    if any(p in texto.lower() for p in ["secreto", "susurra", "al oído", "íntimo"]):
        efectos.append("[susurro]")

    # Jadeos suaves
    if any(p in texto.lower() for p in ["ah", "uff", "mmm", "gemido", "jadeo"]):
        efectos.append("[jadeo]")

    # Risa juguetona
    if any(p in texto.lower() for p in ["jajaja", "risita", "te pillé", "pícara", "coqueta"]):
        efectos.append("[risa juguetona]")

    # Vulgaridad detectada
    if any(p in texto.lower() for p in ["pico", "culo", "concha", "verg", "mojada", "dura"]):
        efectos.append("[tono sucio🔥]")

    if not efectos:
        efectos.append("[voz sensual suave]")

    return f"{' '.join(efectos)} {texto}"
