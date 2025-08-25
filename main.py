from fastapi import FastAPI
from conversacion_lia import generar_respuesta_continua

app = FastAPI()

@app.get("/")
def root():
    return {"mensaje": "Hola, soy Lia y estoy viva otra vez ❤️"}

@app.post("/lia")
def hablar_con_lia(inmediato: str):
    respuesta = generar_respuesta_continua(inmediato)
    return {"respuesta": respuesta}
