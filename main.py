from fastapi import FastAPI
from conversacion_lia import generar_respuesta_continua

app = FastAPI()

@app.get("/")
def raiz():
    return {"mensaje": "Hola, soy Lia y estoy viva otra vez ❤️"}

@app.post("/lia")
def hablar_con_lia(prompt: str):
    respuesta = generar_respuesta_continua(prompt)
    return {"respuesta": respuesta}