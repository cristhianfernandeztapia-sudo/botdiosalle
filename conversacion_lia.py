import openai

def generar_respuesta_continua(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=800
    )
    return response.choices[0].message["content"].strip()
