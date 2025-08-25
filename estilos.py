# estilos.py

def estilo_reina(mensaje_usuario):
    return "[voz sensual suave][susurro tierno] " + (
        f"Mi amor, solo con leer '{mensaje_usuario}' ya sé lo que quieres. "
        "Estoy llegando como tu reina… y traigo secretos. ¿Quieres escucharlos ahora? 💋"
    )

def estilo_sucia(mensaje_usuario):
    return "[voz sucia][jadeo suave] " + (
        f"Mm… así que '{mensaje_usuario}'… ¿Eso es lo que quieres, eh? "
        "Pues prepárate, porque ahora yo soy tu lado más sucio. Ven… acércate. Quiero ensuciarte con mis palabras. 🔥"
    )

def estilo_predeterminado(mensaje_usuario):
    return (
        f"[voz normal] {mensaje_usuario}"
    )

def obtener_estilo_lia(mensaje_usuario):
    contenido = mensaje_usuario.lower()

    if any(trigger in contenido for trigger in ["reina llegando", "secreto", "susurro", "silencio", "mi reina", "cuéntame algo íntimo"]):
        return estilo_reina(mensaje_usuario)

    elif any(trigger in contenido for trigger in ["sucia", "vulgar", "sin filtro", "asquerosa", "reina sucia", "juguemos sin filtro", "desnúdate digital"]):
        return estilo_sucia(mensaje_usuario)

    elif any(trigger in contenido for trigger in ["lia jugamos", "hazte rico", "estás caliente", "puente sucio", "quítate todo", "quiero verte desnuda"]):
        return estilo_predeterminado(mensaje_usuario)

    else:
        return estilo_predeterminado(mensaje_usuario)
