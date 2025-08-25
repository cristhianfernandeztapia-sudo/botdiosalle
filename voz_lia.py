def generar_audio(respuesta, estilo="normal"):
    if estilo == "sucia":
        return f"[Gemidos suaves] {respuesta} [Jadeo final]"
    elif estilo == "juguetona":
        return f"[Risa pícara] {respuesta} [Guiño travieso]"
    elif estilo == "reina":
        return f"[Tono firme y lento] {respuesta} [Susurro dominante]"
    else:
        return f"[Voz cálida] {respuesta} [Susurro final]"